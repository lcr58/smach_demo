#!/usr/bin/env python

import roslib
import rospy, math
import smach
import smach_ros
import sys, time
from numpy import *
import _pyvicon
from geometry_msgs.msg import Twist

# define state Search
class Search(smach.State):
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['found'],
                             output_keys=['x_out','y_out'])
                             
    def execute(self, userdata):
        rospy.loginfo('Executing state Search')
        while not rospy.is_shutdown():
            while (o > -1.99) or (o < o0-2.01):
                (t, x, y, o) = s.getData()
                (t, x, y, o) = [t/100, x/1000, y/1000, o]
                print x, y, o
                twist = Twist()
                if (o > o0+.005):
                    twist.angular.z = -.1
                elif (o < o0-.005):
                    twist.angular.z = .1
                pub.publish(twist)
            if (o < o0+.005) and (o > o0-.005):
                twist.angular.z = 0
                pub.publish(twist)
                userdata.x_out = -.3
                userdata.y_out = -.2
                return 'found'

# define state Drive
class Drive(smach.State):
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['here'],
                             input_keys=['x_in','y_in'])
                             
    def execute(self, userdata):
        rospy.loginfo('Executing state Drive')
        while not rospy.is_shutdown():
            (t, x, y, o) = s.getData()
            (t, x, y, o) = [t/100, x/1000, y/1000, o]
            print x, y, o
            twist = Twist()
            while (x > userdata.x_in+.1) or (x < userdata.x_in-.1) or (y > userdata.y_in+.1) or (y < userdata._in-.1):
                if (x > userdata.x_in+.1):
                    twist.linear.x = -0.08
                elif (x < userdata.x_in-.1):
                    twist.linear.x = 0.08
                if (y > userdata.y_in+.1):
                    twist.linear.y = -0.08
                elif (y < userdata.y_in-.1):
                    twist.linear.y = 0.08
                pub.publish(twist)
            if (x < userdata.x_in+.1 and x > userdata.x_in-.1):
                twist.linear.x = 0
            if (y < userdata.y_in+.1 and y > userdata.y_in-.1):
                twist.linear.y = 0
            pub.publish(twist)
            if (x < userdata.x_in+.1 and x > userdata.x_in-.1 and y < userdata.y_in+.1 and y > userdata.y_in-.1):
                twist.linear.x = 0
                twist.linear.y = 0
                pub.publist(twist)
                return 'here'



def main():
    rospy.init_node('smach_youbot')
    try:
        #open a publisher for the topic
        pub = rospy.Publisher("/cmd_vel", Twist)
        rospy.init_node("LTLMoP_control")
        # for youBot, use /cmd_vel
    except:
        print 'Problem setting up Locomotion Command Node'

    host = "10.0.0.102"
    port = 800
    x = "KUKAyouBot2:main body <t-X>"
    y = "KUKAyouBot2:main body <t-Y>"
    theta = "KUKAyouBot2:main body <a-Z>"

    s = _pyvicon.ViconStreamer()
    s.connect(host, port)
    s.selectStreams(["Time", x, y, theta])
    s.startStreams()

    # Wait for first data to come in
    while s.getData() is None: pass
    
    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['done'])
    sm.userdata.sm_x = 0
    sm.userdata.sm_y = 0
    
    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('Search', Search(),
                               transitions={'found':'Drive'},
                               remapping={'x_out':'sm_x',
                                          'y_out':'sm_y'})
        smach.StateMachine.add('Drive', Drive(),
                               transitions={'here':'done'},
                               remapping={'x_in':'sm_x',
                                          'y_in':'sm_y'})
                                          
    # Execute SMACH plan
    outcome = sm.execute()
    
    
if __name__ == '__main__':
    main()


