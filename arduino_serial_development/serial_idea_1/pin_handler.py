class PinHandler:

    def __init__(self):

        self.pin_array = []

        self.excluded_list = []

        for _ in range(48 * 2):

            self.pin_array.append("0")

    def setRelaysOn(self, relayNumbers):

        for i in relayNumbers:

            self.pin_array[i - 1] = "1"

    def setRelaysOff(self, relayNumbers):

        for i in relayNumbers:

            self.pin_array[i - 1] = "0"

    def excludePins(self, relayNumbers):

        for i in relayNumbers:

            if i not in self.excluded_list:

                self.excluded_list.append(i)

    def undoExcludePins(self, relayNumbers):

        for i in relayNumbers:

            if i in self.excluded_list:

                self.excluded_list.remove(i)

    def setLeachRelays(self, relayNumbers):

        for i in range(48):

            self.pin_array[i] = "0"

        for i in relayNumbers:

            if i not in self.excluded_list:

                self.pin_array[i - 1] = "1"
