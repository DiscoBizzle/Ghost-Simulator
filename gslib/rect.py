

class Rect(object):
    """Re-implement (most of) pygame's Rect class.

    Differences between this and pygame:
     * coordinate system has origin at lower left (like pyglet)
     * Rect((left, bottom), (width, height)) is the only constructor
     * the "missing" clip_ip and fit_ip methods are added
     * added __eq__ and __ne__ methods
     * __nonzero__ requires both height and width to be non-zero to return True
    """

    def __init__(self, pos, size):
        self.left, self.bottom = pos
        self.width, self.height = size

    def __eq__(self, other):
        return (self.bottomright == other.bottomright and
                self.size == other.size)

    def __ne__(self, other):
        return not (self == other)

    def __nonzero__(self):
        return self.w != 0 and self.h != 0

    @property
    def x(self):
        return self.left

    @x.setter
    def x(self, value):
        self.left = value

    @property
    def y(self):
        return self.bottom

    @y.setter
    def y(self, value):
        self.bottom = value

    @property
    def top(self):
        return self.bottom + self.height

    @top.setter
    def top(self, value):
        self.bottom = value - self.height

    @property
    def right(self):
        return self.left + self.width

    @right.setter
    def right(self, value):
        self.left = value - self.height

    @property
    def topleft(self):
        return (self.left, self.top)

    @topleft.setter
    def topleft(self, value):
        (self.left, self.top) = value

    @property
    def bottomleft(self):
        return (self.left, self.bottom)

    @bottomleft.setter
    def bottomleft(self, value):
        (self.left, self.bottom) = value

    @property
    def topright(self):
        return (self.right, self.top)

    @topright.setter
    def topright(self, value):
        (self.right, self.top) = value

    @property
    def bottomright(self):
        return (self.right, self.bottom)

    @bottomright.setter
    def bottomright(self, value):
        (self.right, self.bottom) = value

    @property
    def midtop(self):
        return (self.centerx, self.top)

    @midtop.setter
    def midtop(self, value):
        (self.centerx, self.top) = value

    @property
    def midleft(self):
        return (self.left, self.centery)

    @midleft.setter
    def midleft(self, value):
        (self.left, self.centery) = value

    @property
    def midbottom(self):
        return (self.centerx, self.bottom)

    @midbottom.setter
    def midbottom(self, value):
        (self.centerx, self.bottom) = value

    @property
    def midright(self):
        return (self.right, self.centery)

    @midright.setter
    def midright(self, value):
        (self.right, self.centery) = value

    @property
    def center(self):
        return (self.centerx, self.centery)

    @center.setter
    def center(self, value):
        (self.centerx, self.centery) = value

    @property
    def centerx(self):
        return self.bottom + self.width/2

    @centerx.setter
    def centerx(self, value):
        self.left = value - self.width/2

    @property
    def centery(self):
        return self.bottom + self.height/2

    @centery.setter
    def centery(self, value):
        self.bottom = value - self.height/2

    @property
    def size(self):
        return (self.width, self.height)

    @size.setter
    def size(self, value):
        (self.width, self.height) = value

    @property
    def w(self):
        return self.width

    @w.setter
    def w(self, value):
        self.width = value

    @property
    def h(self):
        return self.height

    @h.setter
    def h(self, value):
        self.height = value

    def copy(self):
        """Return a new Rect with the same position and size."""
        return Rect(self.bottomleft, self.size)

    def move_ip(self, x, y):
        """Same as move, but in-place."""
        self.left += x
        self.bottom += y

    def move(self, x, y):
        """Return a new Rect shifted by (x,y)."""
        res = self.copy()
        res.move_ip(x, y)
        return res

    def inflate_ip(self, x, y):
        """Same as inflate, but in-place."""
        self.width += x
        self.height += y
        self.left -= x/2
        self.bottom -= y/2

    def inflate(self, x, y):
        """Return a new Rect with size changed by (x, y), with center unmoved."""
        res = self.copy()
        res.inflate_ip(x, y)
        return res

    def clamp_ip(self, other):
        """Same as clamp, but in-place."""
        if self.w >= other.w or self.h >= other.h:
            self.center = other.center
            return

        self.left = max(self.left, other.left)
        self.bottom = max(self.bottom, other.bottom)
        self.right = min(self.right, other.right)
        self.top = min(self.top, other.top)

    def clamp(self, other):
        """Return a new Rect moved to fit inside other.

        If self does not fit inside other, it is centred inside the target,
        but its size is not changed.
        """
        res = self.copy()
        res.clamp_ip(other)
        return res

    def clip_ip(self, other):
        """Same as clip, but in-place."""
        if self.right > other.right:
            self.width = self.right - other.right
        if self.top > other.top:
            self.height = self.top - other.top
        if self.left < other.left:
            self.width -= other.left - self.left
            self.left = other.left
        if self.bottom < other.bottom:
            self.height -= other.bottom - self.bottom
            self.bottom = other.bottom

        self.height = max(0, self.height)
        self.width = max(0, self.width)

    def clip(self, other):
        """Return a new Rect cropped to fit inside the other.

        If the Rects do not overlap, a Rect of size 0 is returned.
        """
        res = self.copy()
        res.clip_ip(other)
        return res

    def union_ip(self, other):
        """Same as union, but in-place."""
        new_width = max(self.right, other.right) - min(self.left, other.left)
        new_height = max(self.top, other.top) - min(self.bottom, other.bottom)

        self.left = min(self.left, other.left)
        self.bottom = min(self.bottom, other.bottom)
        self.size = (new_width, new_height)

    def union(self, other):
        """Return a new Rect that completely covers both Rects.

        May include areas not covered by the originals.
        """
        res = self.copy()
        res.union_ip(other)
        return res

    def unionall_ip(self, others):
        """Same as unionall, but in-place."""
        for other in others:
            self.union_ip(other)

    def unionall(self, others):
        """Return a new Rect covering all of self and each of others."""
        res = self.copy()
        res.unionall_ip(others)
        return res

    def fit_ip(self, other):
        """Same as fit, but in-place."""
        if self.height > other.height:
            self.width = self.width * other.height / self.height
            self.height = other.height
        if self.width > other.width:
            self.height = self.height * other.width / self.width
            self.width = other.width

        self.clamp_ip(other)

    def fit(self, other):
        """Return a new Rect moved and rescaled to fit inside the other.

        The aspect ratio of the original Rect is preserved.
        """
        res = self.copy()
        res.fit_ip(other)
        return res

    def normalize(self):
        """Correct negative height or width, without moving the Rect."""
        if self.width < 0:
            self.right = self.left
            self.width = -self.width
        if self.height < 0:
            self.top = self.bottom
            self.height = -self.height

    def contains(self, other):
        """Return True when other is completely contained in self."""
        return other.union(self) == other

    def collidepoint(self, point):
        """Return True when the point is inside the Rect.

        A point on the top or right edge is not inside the Rect.
        """
        return (self.left <= point[0] < self.right and
                self.bottom <= point[1] < self.top)

    def colliderect(self, other):
        """Return True when any portions of the Rects overlap.

        Does not count the edges touching as overlapping.
        """
        return bool(self.clip(other))

    def collidelist(self, others):
        """Return the index of the first Rect in others where there is a
        collision, or -1."""
        for i, other in enumerate(others):
            if self.colliderect(other):
                return i
        return -1

    def collidelistall(self, others):
        """Return the indices of all Rects that collide with self."""
        res = []
        for i, other in enumerate(others):
            if self.colliderect(other):
                res.append(i)
        return res

    def collidedict(self, d):
        """Return the (key, value) pair for the first colliding Rect in d, or None."""
        for k, v in d.iteritems():
            if self.colliderect(v):
                return k, v
        return None

    def collidedictall(self, d):
        """Return a list of all (key, value) pairs which collide with self."""
        res = []
        for k, v in d.iteritems():
            if self.colliderect(v):
                res.append((k, v))
        return res
