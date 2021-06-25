from gi.repository import GObject, RB, Peas


class RbMqttPlugin (GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(RbMqttPlugin, self).__init__()

    def do_activate(self):
        print("RBMQTT represent")

    def do_deactivate(self):
        print("Goodbye RBMQTT")
