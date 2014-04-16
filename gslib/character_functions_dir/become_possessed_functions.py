__author__ = 'Martin'

################################################################################
### possession functions
### These happen when a character is possessed
################################################################################
def im_possessed(obj):
    def func():
        return
        surf = text.speech_bubble("I'm possessed!", 150)
        pos = (obj.dimensions[0]/2,  - surf.get_height())
        obj.flair['possessed'] = (surf, pos)
    func.__name__ = 'im_possessed'
    return func


def flip_state(obj):
    def func():
        obj.state_index = not obj.state_index
    func.__name__ = 'flip_state'
    return func