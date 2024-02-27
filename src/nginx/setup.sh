#!/bin/bash
grep -lr localhost:8000 /usr/share/nginx/html | xargs sed -i "s/localhost:8000/$uri/g"
grep -lr http /usr/share/nginx/html | xargs sed -i "s/http/https/g"
grep -lr httpss /usr/share/nginx/html | xargs sed -i "s/httpss/https/g"

nginx -g "daemon off;"
