class PinHandler:

    def __init__(self):

        self.pin_array = []

        for _ in range(48 * 2):

            self.pin_array.append("0")


    def setLeachRelays(self, relayNumbers):

        for i in range(32):

            self.pin_array[i] = 0

        for j in relayNumbers:

            self.pin_array[j - 1] = 1

    def setElectrowinningRelays(self, relayNumbers):

        for i in range(48, 80):

            self.pin_array[i] = 0

        for j in relayNumbers:

            self.pin_array[j - 1] = 1

    def setRelays(self, relayNumbers):

        for i in relayNumbers:

            self.pin_array[i - 1] = 1

    
