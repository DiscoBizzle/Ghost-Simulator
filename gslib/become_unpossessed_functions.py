__author__ = 'Martin'

################################################################################
### unpossession functions
### These happen when a character is unpossessed
################################################################################

def undo_im_possessed(obj):
    def func():
        return
        if not obj.possessed_by:
            del obj.flair['possessed']
    return func