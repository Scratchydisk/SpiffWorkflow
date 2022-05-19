# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class TransactionSubprocessTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('transaction.bpmn', 'Main_Process')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()

    def testBoundaryNavigation(self):

        nav = self.workflow.get_flat_nav_list()
        self.assertEqual(27, len(nav))
        self.assertNav(nav_item=nav[22], state="WAITING", description="Catch Error 1")
        self.assertNav(nav_item=nav[24], state="WAITING", description="Catch Error None")
        self.assertNav(nav_item=nav[26], state="WAITING", description="Catch Cancel Event")

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'quantity': 2})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()

        nav = self.workflow.get_flat_nav_list()
        self.assertEquals(27, len(nav))
        self.assertNav(nav_item=nav[22], state="CANCELLED", description="Catch Error 1")
        self.assertNav(nav_item=nav[24], state="CANCELLED", description="Catch Error None")
        self.assertNav(nav_item=nav[26], state="CANCELLED", description="Catch Cancel Event")

    def testNormalCompletion(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'quantity': 2})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        self.assertIn('value', self.workflow.last_task.data)

        # Check that workflow and next task completed
        subprocess = self.workflow.get_tasks_from_spec_name('Subprocess')[0]
        self.assertEqual(subprocess.get_state(), TaskState.COMPLETED)
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")[0]
        self.assertEqual(print_task.get_state(), TaskState.COMPLETED)

        # Check that the boundary events were cancelled
        cancel_task = self.workflow.get_tasks_from_spec_name("Catch_Cancel_Event")[0]
        self.assertEqual(cancel_task.get_state(), TaskState.CANCELLED)
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.get_state(), TaskState.CANCELLED)
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.get_state(), TaskState.CANCELLED)


    def testSubworkflowCancelEvent(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)

        # If value == '', we cancel
        ready_tasks[0].update_data({'value': ''})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()

        # If the subprocess gets cancelled, verify that data set there does not persist
        self.assertNotIn('value', self.workflow.last_task.data)

        # Check that we completed the Cancel Task
        cancel_task = self.workflow.get_tasks_from_spec_name("Cancel_Action")[0]
        self.assertEqual(cancel_task.get_state(), TaskState.COMPLETED)

        # And cancelled the remaining tasks
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.get_state(), TaskState.CANCELLED)
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.get_state(), TaskState.CANCELLED)
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")[0]
        self.assertEqual(print_task.get_state(), TaskState.CANCELLED)

    def testSubworkflowErrorCodeNone(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)

        # If quantity == 0, we throw an error with no error code
        ready_tasks[0].update_data({'quantity': 0})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()

        # Check that subprocess data does not persist
        self.assertNotIn('value', self.workflow.last_task.data)

        # The cancel boundary event and print data tasks should be cancelled
        cancel_task = self.workflow.get_tasks_from_spec_name("Catch_Cancel_Event")[0]
        self.assertEqual(cancel_task.get_state(), TaskState.CANCELLED)
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")[0]
        self.assertEqual(print_task.get_state(), TaskState.CANCELLED)

        # We should catch the None Error, but not Error 1
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.get_state(), TaskState.COMPLETED)
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.get_state(), TaskState.CANCELLED)


    def testSubworkflowErrorCodeOne(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)

        # If quantity < 0, we throw 'Error 1'
        ready_tasks[0].update_data({'quantity': -1})
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()

        # Check that subprocess data does not persist
        self.assertNotIn('value', self.workflow.last_task.data)

        # The cancel boundary event and print data tasks should be cancelled
        cancel_task = self.workflow.get_tasks_from_spec_name("Catch_Cancel_Event")[0]
        self.assertEqual(cancel_task.get_state(), TaskState.CANCELLED)
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")[0]
        self.assertEqual(print_task.get_state(), TaskState.CANCELLED)

        # Both boundary events should complete
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.get_state(), TaskState.COMPLETED)
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.get_state(), TaskState.COMPLETED)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TransactionSubprocessTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
