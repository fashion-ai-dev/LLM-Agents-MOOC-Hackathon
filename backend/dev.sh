#!/bin/bash

watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- python app.py
