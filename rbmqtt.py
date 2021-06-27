from gi.repository import GObject, RB, Peas, GLib, Gio, PeasGtk, Gtk
import paho.mqtt.client as mqtt
import rb


class RbMqttPlugin (GObject.Object, Peas.Activatable, PeasGtk.Configurable):
    __gtype_name__ = 'RbMqttPlugin'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(RbMqttPlugin, self).__init__()
        self.settings = None
        self.client = None
        self.plugin_name = "RBMQTT"
        self.settings_timer = 0
        self.server = ""
        self.port = -1
        self.username = ""
        self.password = ""
        self.basetopic = ""

    def do_activate(self):
        print(f'Activating plugin {self.plugin_name}')
        self.settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.rbmqtt")
        self.settings.connect("changed", self.on_settings_changed)
        self.reload_settings()

    def do_deactivate(self):
        print(f'Start deactivating plugin {self.plugin_name}')
        if (self.client):
            self.publish_player_status("inactive")
            shell = self.object
            shell_player = shell.props.shell_player
            shell_player.disconnect(self.psc_id)
            self.psc_id = None
            shell_player.disconnect(self.pc_id)
            self.pc_id = None

            self.disconnect_mqtt()

        if (self.settings):
            self.settings = None

        print(f'Completed deactivating plugin {self.plugin_name}')

    def disconnect_mqtt(self):
        self.client.loop_stop()
        self.client = None

    def connect_mqtt(self):
        if (self.client and self.client.is_connected()):
            self.disconnect_mqtt()

        if (self.settings):
            self.client = mqtt.Client()
            self.client.loop_start()
            self.client.on_connect = self.on_connect
            self.client.username_pw_set(
                self.username, self.password)
            self.client.connect_async(self.server, self.port, 60)
            self.client.loop_start()

    def reload_settings(self):
        if (self.settings):
            self.server = self.settings.get_string("mqtt-server")
            self.port = int(self.settings.get_string("mqtt-port"))
            self.username = self.settings.get_string("mqtt-username")
            self.password = self.settings.get_string("mqtt-password")
            self.basetopic = self.settings.get_string("base-topic")
            if (self.server and self.port > 0):
                self.connect_mqtt()
        self.settings_timer = 0
        return False

    def on_settings_changed(self, settings, key):
        if (self.settings_timer > 0):
            GLib.source_remove(self.settings_timer)
            self.settings_timer = 0
        self.settings_timer = GLib.timeout_add_seconds(5, self.reload_settings)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {str(rc)}")

        if (self.client.is_connected()):
            shell = self.object
            shell_player = shell.props.shell_player
            self.psc_id = shell_player.connect(
                "playing-song-changed", self.playing_song_changed)
            self.pc_id = shell_player.connect("playing-changed",
                                              self.playing_changed)
            self.publish_song_details(shell_player.get_playing_entry())
            playing = shell_player.get_playing()[1]
            self.publish_player_status("playing" if playing else "paused")

    def playing_changed(self, sp, playing):
        self.publish_player_status("playing" if playing else "paused")

    def playing_song_changed(self, shell, entry):
        self.publish_song_details(entry)

    def publish_subtopic(self, subtopic, payload):
        if (self.client):
            topic = f'{self.basetopic}/{subtopic}'
            self.client.publish(topic, payload)

    def publish_song_details(self, entry):
        if (entry is None):
            artist = ""
            album = ""
            title = ""
        else:
            artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
            album = entry.get_string(RB.RhythmDBPropType.ALBUM)
            title = entry.get_string(RB.RhythmDBPropType.TITLE)
        self.publish_subtopic("artist", artist)
        self.publish_subtopic("album", album)
        self.publish_subtopic("title", title)

    def publish_player_status(self, status):
        self.publish_subtopic("status", status)

    mqtt_server_entry = GObject.Property(type=Gtk.Entry, default=None)
    mqtt_port_entry = GObject.Property(type=Gtk.Entry, default=None)
    mqtt_username_entry = GObject.Property(type=Gtk.Entry, default=None)
    mqtt_password_entry = GObject.Property(type=Gtk.Entry, default=None)
    base_topic_entry = GObject.Property(type=Gtk.Entry, default=None)

    def do_create_configure_widget(self):
        self.settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.rbmqtt")

        ui_file = rb.find_plugin_file(self, "rbmqtt-prefs.ui")
        self.builder = Gtk.Builder()
        self.builder.add_from_file(ui_file)

        content = self.builder.get_object("rbmqtt-prefs")

        self.mqtt_server_entry = self.builder.get_object("mqtt-server")
        self.settings.bind("mqtt-server", self.mqtt_server_entry, "text", 0)

        self.mqtt_port_entry = self.builder.get_object("mqtt-port")
        self.settings.bind("mqtt-port", self.mqtt_port_entry, "text", 0)

        self.mqtt_username_entry = self.builder.get_object("mqtt-username")
        self.settings.bind(
            "mqtt-username", self.mqtt_username_entry, "text", 0)

        self.mqtt_password_entry = self.builder.get_object("mqtt-password")
        self.settings.bind(
            "mqtt-password", self.mqtt_password_entry, "text", 0)

        self.base_topic_entry = self.builder.get_object("base-topic")
        self.settings.bind(
            "base-topic", self.base_topic_entry, "text", 0)

        return content
