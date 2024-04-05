import inspect

from util import *
from objects import *
from states_definition import *
from animation import *

class Goblin(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 0.1,
            drops = [(11, 0.5), (11, 0.5), (12, 0.2), (13, 0.01)],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "goblin.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step",
                            3 : "step"
                        }
                    ))
                ]
            ),
            bloodColour = (45, 69, 7)
        )

class Skeleton(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 15,
            speed = 0.1,
            drops = [(3, 1), (3, 0.5), (3, 0.2)],
            attackDamage = 7,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Skeleton_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "skeleton.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step",
                            3 : "step"
                        }
                    )),
                    ("dead", Animation(
                        app,
                        0,
                        32
                    ))
                ]
            ),
            bloodColour = None
        )

class BigSlime(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 30,
            speed = 0.05,
            drops = [],
            attackDamage = 7,
            pos = pos,
            radius = 10,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_BigSlime_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "bigslime.png",
                [
                    ("idle", Animation(
                        app,
                        0,
                        0,
                    )),
                    ("moving", Animation(
                        app,
                        0.2,
                        0, 1, 2, 3, 4, 5, 6, 7
                    ))
                ]
            ),
            bloodColour = (33, 117, 45)
        )

class Slime(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.15,
            drops = [
                [31, 1],
                [32, 0.5],
                [33, 0.5],
                [34, 0.5],
                [35, 0.5],
                [36, 0.5],
                [37, 0.5]
            ],
            attackDamage = 2,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "smallslime.png",
                [
                    ("idle", Animation(
                        app,
                        0,
                        0,
                    )),
                    ("moving", Animation(
                        app,
                        0.2,
                        0, 1, 2, 3, 4, 5
                    ))
                ]
            ),
            bloodColour = (33, 117, 45)
        )

class Bat(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.1,
            drops = [],
            attackDamage = 2,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "bat.png",
                [
                    ("idle", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("moving", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    ))
                ]
            )
        )

class Python(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 1,
            drops = [],
            attackDamage = 2,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Python_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "python.png",
                [
                    ("idle", RotationalAnimation(
                        self,
                        0,
                        *framePresets["idle"],
                    )),
                    ("moving", RotationalAnimation(
                        self,
                        0.1,
                        *framePresets["moving"],
                    ))
                ]
            )
        )

class Spider(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 5,
            speed = 0.16,
            drops = [],
            attackDamage = 0.1,
            pos = pos,
            radius = 3,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "spider.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0],
                        [2]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.25,
                        [0, 1],
                        [2, 3]
                    ))
                ]
            )
        )

class MineZombie(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 25,
            speed = 0.07,
            drops = [
                [19, 0.5]
            ],
            attackDamage = 7,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "minezombie.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step2"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.13,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step2",
                            3 : "step2"
                        }
                    ))
                ]
            )
        )

class Viper(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Python_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "viper.png",
                [
                    ("idle", RotationalAnimation(
                        self,
                        0,
                        *framePresets["idle"],
                    )),
                    ("moving", RotationalAnimation(
                        self,
                        0.1,
                        *framePresets["moving"],
                    ))
                ]
            ),
            attackStatusEffect = 0,
            attackStatusEffectChance = 0.5
        )

class Ultrabat(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 0.1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "ultrabat.png",
                [
                    ("idle", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("moving", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    ))
                ]
            ),
            attackStatusEffect = 0,
            attackStatusEffectChance = 0.5
        )

class Ultraspider(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 5,
            speed = 0.13,
            drops = [],
            attackDamage = 0.1,
            pos = pos,
            radius = 3,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "ultraspider.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0],
                        [2]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.25,
                        [0, 1],
                        [2, 3]
                    ))
                ]
            ),
            attackStatusEffect = 0,
            attackStatusEffectChance = 0.5
        )

class BoneBat(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Skeleton_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "bonebat.png",
                [
                    ("idle", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("moving", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("dead", Animation(
                        app,
                        0,
                        4
                    ))
                ]
            ),
            bloodColour = None
        )

class MushroomMan(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 0.1,
            drops = [(0, 0.4), (0, 0.4), (0, 0.4)],
            attackDamage = 7,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "mushroomman.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step",
                            3 : "step"
                        }
                    ))
                ]
            ),
            bloodColour = (86, 42, 38),
            attackStatusEffect = 3,
            attackStatusEffectChance = 0.5
        )

class MushroomBat(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.1,
            drops = [(0, 0.4), (0, 0.4)],
            attackDamage = 5,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "mushroombat.png",
                [
                    ("idle", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("moving", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    ))
                ]
            ),
            bloodColour = (86, 42, 38),
            attackStatusEffect = 3,
            attackStatusEffectChance = 0.5
        )

class SporeCloud(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.05,
            drops = [],
            attackDamage = 0,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_SporeCloud_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "sporecloud.png",
                [
                    ("idle", Animation(
                        app,
                        0.1,
                        0, 1, 2, 3, 4, 5
                    )),
                    ("moving", Animation(
                        app,
                        0.1,
                        0, 1, 2, 3, 4, 5
                    ))
                ]
            ),
            invulnerable = True,
            attackStatusEffect = 3
        )

class SnowBat(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "snowbat.png",
                [
                    ("idle", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("moving", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    ))
                ]
            ),
            attackStatusEffect = 2
        )

class Snowman(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 0.1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "snowman.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step",
                            3 : "step"
                        }
                    ))
                ]
            ),
            bloodColour = (255, 255, 255),
            attackStatusEffect = 2
        )

class Yeti(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 25,
            speed = 0.07,
            drops = [],
            attackDamage = 7,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "yeti.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step2"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.13,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step2",
                            3 : "step2"
                        }
                    ))
                ]
            )
        )

class Horseman(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 10,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Horseman_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "horseman.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0], [2],
                        sounds = {
                            0 : "step2"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.15,
                        [1, 0], [3, 2],
                        sounds = {
                            0 : "step2"
                        }
                    ))
                ]
            )
        )
    
    def damage(self, by, attacker):
        if super().damage(by, attacker):
            # When the enemy gets damaged, play an extra sound.
            self.app.soundPlayer.stop_group(self)
            self.app.soundPlayer.play_preset_positional_sound(
                "horsehurt",
                pos = self.pos,
                group = self
            )
            return True
        return False

class Rockman(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 25,
            speed = 0.07,
            drops = [],
            attackDamage = 7,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "rockman.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step2"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.13,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step2",
                            3 : "step2"
                        }
                    ))
                ]
            ),
            bloodColour = (99, 82, 58)
        )

class LavaBubble(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.09,
            drops = [],
            attackDamage = 0,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_SporeCloud_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "lavabubble.png",
                [
                    ("idle", Animation(
                        app,
                        0.2,
                        0, 1, 2, 3, 4, 5, 6, 7
                    )),
                    ("moving", Animation(
                        app,
                        0.2,
                        0, 1, 2, 3, 4, 5, 6, 7
                    ))
                ]
            ),
            invulnerable = True,
            attackStatusEffect = 4
        )

class Lavaman(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 25,
            speed = 0.07,
            drops = [],
            attackDamage = 7,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "lavaman.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step2"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.13,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step2",
                            3 : "step2"
                        }
                    ))
                ]
            ),
            bloodColour = None,
            attackStatusEffect = 4
        )

class FireBat(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 20,
            speed = 0.1,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "firebat.png",
                [
                    ("idle", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    )),
                    ("moving", Animation(
                        app,
                        0.25,
                        0, 1, 2, 3
                    ))
                ]
            ),
            attackStatusEffect = 4,
            attackStatusEffectChance = 0.5
        )

class Scientist(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.12,
            drops = [],
            attackDamage = 0,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Scientist_Idle,
                    "running" : State_Scientist_Running
                }
            },
            animationManager = AnimationManager(
                app,
                "scientist.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step",
                            3 : "step"
                        }
                    ))
                ]
            )
        )

class SecurityRobot(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 30,
            speed = 0.12,
            drops = [],
            attackDamage = 8,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "securityrobot.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step2"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step2",
                            3 : "step2"
                        }
                    ))
                ]
            ),
            bloodColour = (0, 0, 0)
        )

class TinyRobot(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 10,
            speed = 0.13,
            drops = [],
            attackDamage = 0,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "tinyrobot.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0], [1], [2], [3], [4], [5], [6], [7]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0,
                        [0], [1], [2], [3], [4], [5], [6], [7]
                    ))
                ]
            ),
            bloodColour = (0, 0, 0),
            attackStatusEffect = 5
        )

class MangledRobot(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 30,
            speed = 0.08,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "mangledrobot.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0.2,
                        [0, 0, 0, 1, 0, 1, 0],
                        [2, 2, 2, 3, 2, 3, 2],
                        [4, 4, 4, 5, 4, 5, 4],
                        [6, 6, 6, 7, 6, 7, 6],
                        [8, 8, 8, 9, 8, 9, 8],
                        [10, 10, 10, 11, 10, 11, 10],
                        [12, 12, 12, 13, 12, 13, 12],
                        [14, 14, 14, 15, 14, 15, 14],
                        sounds = {
                            3 : "zap",
                            5 : "zap"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        [0, 0, 0, 1, 0, 1, 0],
                        [2, 2, 2, 3, 2, 3, 2],
                        [4, 4, 4, 5, 4, 5, 4],
                        [6, 6, 6, 7, 6, 7, 6],
                        [8, 8, 8, 9, 8, 9, 8],
                        [10, 10, 10, 11, 10, 11, 10],
                        [12, 12, 12, 13, 12, 13, 12],
                        [14, 14, 14, 15, 14, 15, 14],
                        sounds = {
                            3 : "zap",
                            5 : "zap"
                        }
                    ))
                ]
            ),
            bloodColour = (39, 14, 136),
            attackStatusEffect = 5,
            attackStatusEffectChance = 0.5
        )

class MangledAnimal(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 30,
            speed = 0.12,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 6,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "mangledanimal.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0], [3],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        [0, 2, 1], [3, 5, 4],
                        sounds = {
                            0 : "step"
                        }
                    ))
                ]
            ),
            attackStatusEffect = 6,
            attackStatusEffectChance = 0.5,
            bloodColour = (129, 35, 195)
        )

class Ghoul(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 50,
            speed = 0.1,
            drops = [],
            attackDamage = 15,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "ghoul.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0], [1], [2], [3], [4], [5], [6], [7]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0,
                        [0], [1], [2], [3], [4], [5], [6], [7]
                    ))
                ]
            ),
            bloodColour = (95, 27, 143),
            attackStatusEffect = 6,
            attackStatusEffectChance = 0.5
        )

class Reaper(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 999,
            speed = 0.08,
            drops = [],
            attackDamage = 49,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "reaper.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0.1,
                        [0, 1, 2, 3], [4, 5, 6, 7]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.1,
                        [0, 1, 2, 3], [4, 5, 6, 7]
                    ))
                ]
            ),
            bloodColour = (8, 1, 24)
        )

class Demon1(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 40,
            speed = 0.12,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "demon.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0], [3],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        [0, 1, 1, 2], [3, 4, 4, 5],
                        sounds = {
                            3 : "step"
                        }
                    ))
                ]
            )
        )

class Demon2(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 40,
            speed = 0.08,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_SporeCloud_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "skull.png",
                [
                    ("idle", Animation(
                        app,
                        0,
                        0
                    )),
                    ("moving", Animation(
                        app,
                        0,
                        0
                    ))
                ]
            )
        )

class Demon3(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 40,
            speed = 0.12,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_SporeCloud_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "flyingdemon.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0.2,
                        [0, 1, 2, 3], [4, 5, 6, 7]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        [0, 1, 2, 3], [4, 5, 6, 7]
                    ))
                ]
            )
        )

class Demon4(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 40,
            speed = 0.12,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "demon2.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        [0], [3],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        [0, 1, 1, 2], [3, 4, 4, 5],
                        sounds = {
                            3 : "step"
                        }
                    ))
                ]
            )
        )

class Demon5(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 40,
            speed = 0.08,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_SporeCloud_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "skull2.png",
                [
                    ("idle", Animation(
                        app,
                        0,
                        0
                    )),
                    ("moving", Animation(
                        app,
                        0,
                        0
                    ))
                ]
            )
        )

class Demon6(Entity):
    def __init__(self, app, pos):
        super().__init__(
            app,
            maxHp = 40,
            speed = 0.12,
            drops = [],
            attackDamage = 5,
            pos = pos,
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Dead
                },
                "movement" : {
                    "idle" : State_Idle,
                    "following" : State_SporeCloud_Following
                },
                "attacks" : {
                    "notAttacking" : State_NotAttacking,
                    "attacking" : State_Attacking
                }
            },
            animationManager = AnimationManager(
                app,
                "flyingdemon2.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0.2,
                        [0, 1, 2, 3], [4, 5, 6, 7]
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        [0, 1, 2, 3], [4, 5, 6, 7]
                    ))
                ]
            )
        )

# This is a list of all of the classes in this file.
# It allows for the classes to be accessed using a index, which makes
# defining which enemies should be in a level in a .json file easy, as
# you just need to provide an index.
classes = [i for i in globals().values() if inspect.isclass(i) and i.__module__ == __name__]