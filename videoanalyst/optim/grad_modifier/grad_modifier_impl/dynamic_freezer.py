# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
import json
import re

import numpy as np
import cv2

import torch
from torch import nn

from yacs.config import CfgNode

from ..grad_modifier_base import TRACK_GRAD_MODIFIERS, VOS_GRAD_MODIFIERS, GradModifierBase
# from ...optimizer.optimizer_base import OptimizerBase
from .utils.freeze import apply_freeze_schedule

@TRACK_GRAD_MODIFIERS.register
@VOS_GRAD_MODIFIERS.register
class DynamicFreezer(GradModifierBase):
    r"""
    Learning rate scheduler, including:
    - learning rate adjusting
    - learning rate multiplying

    Hyper-parameters
    ----------------
    phases: Dict

    """
    default_hyper_params = dict(
        schedule=[],
    )
    def __init__(self, ) -> None:
        super().__init__()

    def update_params(self) -> None:
        r"""
        Resolve dynamic freezing schedule
        """
        cfg = self._hyper_params["schedule"]
        if len(cfg) > 0:
            schedule = list()
            for freeze_str in cfg:
                # from IPython import embed;embed()
                mult_cfg = json.loads(freeze_str)
                compiled_regex = re.compile(mult_cfg["regex"])
                mult_cfg["compiled_regex"] = compiled_regex
                schedule.append(mult_cfg)
            self._state["schedule"] = schedule


    # def set_optimizer(self, optimizer) -> None:
    #     super(LRScheduler, self).set_optimizer(optimizer)
    #     if self._lr_multiplier is not None:
    #         optimizer._param_groups_divider = self._lr_multiplier.divide_into_param_groups

    def modify_grad(self, module: nn.Module, epoch: int, iteration: int=-1):
        if (iteration < 0) and ("schedule" in self._state):
            # epoch-level scheduling
            apply_freeze_schedule(module, epoch, self._state["schedule"])
        else:
            # iteration-level scheduling
            pass