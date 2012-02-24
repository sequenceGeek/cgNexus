#!/bin/bash

#stage, commit, and push in one go
eval "git add ."
eval "git commit -a -m $1"
eval "git push -u origin master"

