#!/bin/bash

SCRIPT_NAME=`basename "$0"`
SCRIPT_PATH=${0%`basename "$0"`}
PLUGIN_PATH="${HOME}/.local/share/rhythmbox/plugins/rbmqtt/"
SCHEMA_PATH="${HOME}/.local/share/glib-2.0/schemas/"
GLIB_SCHEME="org.gnome.rhythmbox.plugins.rbmqtt.gschema.xml"
GLIB_DIR="/usr/share/glib-2.0/schemas/"

# copy plugin files
mkdir -p $PLUGIN_PATH
cp "${SCRIPT_PATH}/rbmqtt.plugin" "$PLUGIN_PATH"
cp "${SCRIPT_PATH}/rbmqtt.py" "$PLUGIN_PATH"
#cp "${SCRIPT_PATH}/rbmqttconfig.py" "$PLUGIN_PATH"
cp "${SCRIPT_PATH}/rbmqtt-prefs.ui" "$PLUGIN_PATH"

# update settings schema
mkdir -p $SCHEMA_PATH
cp "${SCRIPT_PATH}/org.gnome.rhythmbox.plugins.rbmqtt.gschema.xml" "$SCHEMA_PATH"
glib-compile-schemas "$SCHEMA_PATH"