# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import os

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnValidator, full_tag, ValidationException

from SpiffWorkflow.bpmn.specs.events.EndEvent import EndEvent
from SpiffWorkflow.bpmn.specs.events.StartEvent import StartEvent
from SpiffWorkflow.bpmn.specs.events.IntermediateEvent import IntermediateThrowEvent, BoundaryEvent, IntermediateCatchEvent

from SpiffWorkflow.spiff.specs.none_task import NoneTask
from SpiffWorkflow.spiff.specs.manual_task import ManualTask
from SpiffWorkflow.spiff.specs.user_task import UserTask
from SpiffWorkflow.spiff.specs.script_task import ScriptTask
from SpiffWorkflow.spiff.specs.subworkflow_task import SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.spiff.specs.service_task import ServiceTask
from SpiffWorkflow.spiff.specs.events.event_types import SendTask, ReceiveTask
from SpiffWorkflow.spiff.specs.business_rule_task import BusinessRuleTask
from SpiffWorkflow.spiff.parser.task_spec import (
    SpiffTaskParser,
    SubWorkflowParser,
    CallActivityParser,
    ServiceTaskParser,
    ScriptTaskParser,
    BusinessRuleTaskParser
)
from SpiffWorkflow.spiff.parser.event_parsers import (SpiffStartEventParser, SpiffEndEventParser, SpiffBoundaryEventParser,
    SpiffIntermediateCatchEventParser, SpiffIntermediateThrowEventParser, SpiffSendTaskParser, SpiffReceiveTaskParser)


from SpiffWorkflow.spiff.parser.task_spec import BusinessRuleTaskParser

SPIFF_XSD = os.path.join(os.path.dirname(__file__), 'schema', 'spiffworkflow.xsd')
VALIDATOR = BpmnValidator(imports={'spiffworkflow': SPIFF_XSD})


class SpiffBpmnParser(BpmnDmnParser):

    OVERRIDE_PARSER_CLASSES = {
        full_tag('task'): (SpiffTaskParser, NoneTask),
        full_tag('userTask'): (SpiffTaskParser, UserTask),
        full_tag('manualTask'): (SpiffTaskParser, ManualTask),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('subProcess'): (SubWorkflowParser, SubWorkflowTask),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('serviceTask'): (ServiceTaskParser, ServiceTask),
        full_tag('startEvent'): (SpiffStartEventParser, StartEvent),
        full_tag('endEvent'): (SpiffEndEventParser, EndEvent),
        full_tag('boundaryEvent'): (SpiffBoundaryEventParser, BoundaryEvent),
        full_tag('intermediateCatchEvent'): (SpiffIntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (SpiffIntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('sendTask'): (SpiffSendTaskParser, SendTask),
        full_tag('receiveTask'): (SpiffReceiveTaskParser, ReceiveTask),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask)
    }
