#!/usr/bin/env bash
# Smoke test del gemelo digital (corre DENTRO del contenedor waver_twin).
# Valida: build, unit tests, xacro de los 3 modelos, y un test E2E:
# el nodo waver_arm (mock) sube el torso 140 mm y TF lo confirma.
set -e
source /opt/ros/humble/setup.bash

echo '=== 1/4 colcon build ==='
cd /ros2_ws
colcon build --symlink-install
source install/setup.bash

echo '=== 2/4 pruebas unitarias (servo_map / regla de oro) ==='
python3 -m pytest src/waver_arm/test/ -q

echo '=== 3/4 xacro de los 3 modelos ==='
# xacro: binario ROS si existe; si no, módulo Python (instalable por pip
# o montado como vendor con PYTHONPATH — imágenes viejas sin pip)
xacro_run() {
  if command -v xacro >/dev/null; then
    xacro "$1"
  else
    python3 -c 'import sys, xacro; print(xacro.process_file(sys.argv[1]).toxml())' "$1"
  fi
}
for m in arm_standalone waver_crab waver_crab_sim; do
  xacro_run "$(ros2 pkg prefix waver_arm_description)/share/waver_arm_description/urdf/${m}.urdf.xacro" > "/tmp/${m}.urdf"
  echo "  ${m}: $(grep -o '<joint' /tmp/${m}.urdf | wc -l) joints ✓"
done

echo '=== 4/4 E2E: robot_state_publisher + waver_arm mock + TF ==='
# el URDF va por params-file (pasarlo por -p en CLI rompe el parser de rcl)
python3 - <<'EOF'
import yaml
urdf = open('/tmp/waver_crab.urdf').read()
yaml.safe_dump(
    {'robot_state_publisher': {'ros__parameters': {'robot_description': urdf}}},
    open('/tmp/rsp_params.yaml', 'w'))
EOF
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args --params-file /tmp/rsp_params.yaml &
RSP=$!
ros2 run waver_arm arm_controller &
ARM=$!
sleep 4

echo '--- pose inicial (torso abajo) ---'
Z0=$(timeout 10 ros2 run tf2_ros tf2_echo base_footprint left_arm_tool0 2>/dev/null \
     | grep -m1 'Translation' | sed 's/.*, \([0-9.]*\)\].*/\1/')
echo "  tool0 z inicial = ${Z0} (esperado ~0.737)"

echo '--- comando: torso a 0.14 m (rampa L16 = 7 s) ---'
ros2 topic pub --once /waver_arm/command sensor_msgs/msg/JointState \
  "{name: [torso_lift_joint], position: [0.14]}"
sleep 9

Z1=$(timeout 10 ros2 run tf2_ros tf2_echo base_footprint left_arm_tool0 2>/dev/null \
     | grep -m1 'Translation' | sed 's/.*, \([0-9.]*\)\].*/\1/')
echo "  tool0 z final = ${Z1} (esperado ~0.877)"

kill $RSP $ARM 2>/dev/null || true

python3 - "$Z0" "$Z1" <<'EOF'
import sys
z0, z1 = float(sys.argv[1]), float(sys.argv[2])
assert abs(z0 - 0.737) < 0.005, f'z inicial {z0} != 0.737'
assert abs(z1 - 0.877) < 0.005, f'z final {z1} != 0.877'
assert abs((z1 - z0) - 0.140) < 0.005, 'la carrera no es 140 mm'
print(f'\n✅ SMOKE TEST OK: el torso subió {1000*(z1-z0):.1f} mm por TF')
EOF
