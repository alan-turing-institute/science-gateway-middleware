#!/bin/bash

curl -X PUT http://localhost:8000/run/job -d @job_template.json
