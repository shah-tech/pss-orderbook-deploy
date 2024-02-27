#!/bin/bash
grep -lr localhost:8000 /usr/share/nginx/html | xargs sed -i "s/localhost:8000/$uri/g"

nginx -g "daemon off;"
