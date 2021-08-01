# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 10:12:04 2021

@author: yf_choong
"""

import os

if not os.path.exists('DataFolder'):
    os.makedirs('DataFolder')
if not os.path.exists('ResultFolder'):
    os.makedirs('ResultFolder')

print("Setup Completed")