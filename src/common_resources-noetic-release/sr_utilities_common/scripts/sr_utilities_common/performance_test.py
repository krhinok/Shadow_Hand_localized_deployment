#!/usr/bin/python
#
# Copyright 2019, 2022 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy
import rospy
from sr_utilities.hand_finder import HandFinder
from diagnostic_msgs.msg import DiagnosticArray
from sr_robot_msgs.msg import EthercatDebug


class PerformanceTest:
    def __init__(self):
        rospy.loginfo("Performance test started")
        self._hand_finder = HandFinder()
        self._hand_e = self._hand_finder.hand_e_available()
        self._hand_h = self._hand_finder.hand_h_available()
        rospy.loginfo(f"Hand E available: {self._hand_e}")
        rospy.loginfo(f"Hand H available: {self._hand_h}")

        rospy.Subscriber("/diagnostics_agg", DiagnosticArray, self._diagnostics_agg_callback)
        if self._hand_e:
            rospy.Subscriber("/rh/debug_etherCAT_data", EthercatDebug, self._ethercat_data_hand_e_callback)

        self.total_control_loop_overruns = 0
        self.max_recent_control_loop_overruns = 0
        self.total_invalid_packets = []
        self.max_invalid_packets_recent = []
        self.invalid_hand_e_packets_total = 0
        self._old_invalid_hand_e_packets = 0
        self.max_invalid_hand_e_packets_recent = 0
        self._start_hand_e_ethercat_time = rospy.get_time()

    def _diagnostics_agg_callback(self, diagnostics_full_msg):
        diagnostics_control_loop_msg = None
        diagnostics_ethercat_msg_list = []

        for msg in diagnostics_full_msg.status:
            if msg.name == "/Realtime Control Loop/Realtime Control Loop":
                diagnostics_control_loop_msg = msg

            if msg.name.startswith("/EtherCat/EtherCAT Slaves/H0_"):
                diagnostics_ethercat_msg_list.append(msg)

        self._set_control_loop_values(diagnostics_control_loop_msg)
        if self._hand_h:
            self._set_ethercat_hand_h_values(diagnostics_ethercat_msg_list)

    def _ethercat_data_hand_e_callback(self, diagnostics_ethercat_msg):
        if diagnostics_ethercat_msg.motor_data_type.data == 0:
            self.invalid_hand_e_packets_total += 1
        if rospy.get_time() - self._start_hand_e_ethercat_time > 1.0:
            self._start_hand_e_ethercat_time = rospy.get_time()
            invalid_hand_e_packets_recent = self.invalid_hand_e_packets_total - self._old_invalid_hand_e_packets
            self._old_invalid_hand_e_packets = self.invalid_hand_e_packets_total
            if invalid_hand_e_packets_recent > self.max_invalid_hand_e_packets_recent:
                self.max_invalid_hand_e_packets_recent = invalid_hand_e_packets_recent

    def _set_ethercat_hand_h_values(self, diagnostics_ethercat_msg_list):
        invalid_packets_total_list = []
        invalid_packets_recent_list = []
        for diagnostics_ethercat_msg in diagnostics_ethercat_msg_list:
            for value_list in diagnostics_ethercat_msg.values:
                if value_list.key == "Invalid Packets Total":
                    invalid_packets_total_list.append(float(value_list.value))
                if value_list.key == "Invalid Packets Recent":
                    invalid_packets_recent_list.append(float(value_list.value))
        if not self.max_invalid_packets_recent:
            self.max_invalid_packets_recent = [0] * len(invalid_packets_recent_list)
        for i in range(len(invalid_packets_recent_list)):
            if invalid_packets_recent_list[i] > self.max_invalid_packets_recent[i]:
                self.max_invalid_packets_recent[i] = invalid_packets_recent_list[i]
        self.total_invalid_packets = deepcopy(invalid_packets_total_list)

    def _set_control_loop_values(self, diagnostics_control_loop_msg):
        for value_list in diagnostics_control_loop_msg.values:
            if value_list.key == "Control Loop Overruns":
                self.total_control_loop_overruns = float(value_list.value)
            if value_list.key == "Recent Control Loop Overruns":
                recent_control_loop_overruns = float(value_list.value)
                if recent_control_loop_overruns > self.max_recent_control_loop_overruns:
                    self.max_recent_control_loop_overruns = recent_control_loop_overruns

    def _print_results(self):
        rospy.loginfo(f"Control Loop Overruns: {self.total_control_loop_overruns}")
        rospy.loginfo(f"Max Recent Control Loop Overruns: {self.max_recent_control_loop_overruns}")
        if self._hand_h:
            for i, value in enumerate(self.total_invalid_packets):
                rospy.loginfo(f"Invalid Packets Total in finger {i}: {value}")
            for i, value in enumerate(self.max_invalid_packets_recent):
                rospy.loginfo(f"Max Invalid Packets Recent in finger {i}: {value}")
        else:
            rospy.loginfo(f"Invalid Packets Total: {self.invalid_hand_e_packets_total}")
            rospy.loginfo(f"Max Invalid Packets Recent: {self.max_invalid_hand_e_packets_recent}")

    def _check_threshold_validity(self):
        total_control_loop_overruns_threshold = rospy.get_param('~total_control_loop_overruns_threshold', 1)
        max_recent_control_loop_overruns_threshold = rospy.get_param('~max_recent_control_loop_overruns_threshold', 1)
        total_invalid_packets_threshold = rospy.get_param('~total_invalid_packets_threshold', 1)
        max_invalid_packets_recent_threshold = rospy.get_param('~max_invalid_packets_recent_threshold', 1)

        pass_flag = True
        if self.total_control_loop_overruns > total_control_loop_overruns_threshold:
            rospy.logerr("Total control loop overruns have exceeded the threshold")
            pass_flag = False

        if self.max_recent_control_loop_overruns > max_recent_control_loop_overruns_threshold:
            rospy.logerr("Max recent control loop overruns have exceeded the threshold")
            pass_flag = False

        if self._hand_h:
            for i in range(len(self.total_invalid_packets)):
                if self.total_invalid_packets[i] > total_invalid_packets_threshold:
                    rospy.logerr(f"Total invalid packets have exceeded the threshold on finger {i}")
                    pass_flag = False
            for i in range(len(self.max_invalid_packets_recent)):
                if self.max_invalid_packets_recent[i] > max_invalid_packets_recent_threshold:
                    rospy.logerr(f"Max recent invalid packets have exceeded the threshold on finger {i}")
                    pass_flag = False
        else:
            if self.invalid_hand_e_packets_total > total_invalid_packets_threshold:
                rospy.logerr("Total invalid packets have exceeded the threshold")
                pass_flag = False
            if self.max_invalid_hand_e_packets_recent > max_invalid_packets_recent_threshold:
                rospy.logerr("Max recent invalid packets have exceeded the threshold")
                pass_flag = False

        if pass_flag:
            green_color = "\033[92m"
            end_color = "\033[0m"
            rospy.loginfo(f"{green_color}Performance Test: PASSED{end_color}")
        else:
            rospy.logerr("Performance Test: FAILED")

    def run(self, duration=20.0):
        if not self._hand_h and not self._hand_e:
            rospy.logerr("No hand was found!!!")
            return False
        start_time = rospy.get_time()
        time = 0.0
        while time < duration and not rospy.is_shutdown():
            time = rospy.get_time() - start_time
            rospy.sleep(0.1)

        self._print_results()
        self._check_threshold_validity()


if __name__ == "__main__":
    rospy.init_node('performance_test', anonymous=True)
    test_duration = rospy.get_param('~test_duration', 20.0)
    pt = PerformanceTest()
    pt.run(duration=test_duration)
