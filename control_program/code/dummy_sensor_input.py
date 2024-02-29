class DummySensorInput:

    def __init__(self):

        self.dummy_sensors = dict()

    def get_dummy_state(self, sensor):

        if sensor in self.dummy_sensors:

            return self.dummy_sensors[sensor]

        else:

            self.dummy_sensors[sensor] = int(input(f"Provide dummy value for {sensor}: "))

            return self.dummy_sensors[sensor]
