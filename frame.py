from show import show


class frame:
    """Encapsulated the state variables and commands of the frame. 
    Intended to be used as a singleton.  Singleton not enforeced."""

    activeshow = show()
    txtoverlay_isvisible = -1
    shows = []

    def debug(this):
        print "Debug frame 1: %s" % this.txtoverlay_isvisible
