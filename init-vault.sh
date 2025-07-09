#!/bin/sh
sleep 3

vault kv put secret/database/testvault username=testvault password=motdepasse123
