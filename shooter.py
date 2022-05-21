from ursina import *
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
app = Ursina()
random.seed(0)
Entity.default_shader = lit_with_shadows_shader
ground = Entity(model='plane', collider='box', scale=(200,1,200), texture='stone.jpg', texture_scale=(4,4))
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
gun = Entity(model='gun.obj', parent=camera.ui, position=(0.3,-0.2),rotation=(-5,-12,-4),scale=.2,color=color.black,on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1.5, world_scale=.5, model='quad', color=color.yellow, enabled=False)
shootables_parent = Entity()
mouse.traverse_target = shootables_parent
wall1=Entity(
model='cube',
texture='wall',
collider='cube',
scale='80,0,80',
position=(80,0,80),
color=color.gray
)
wall2=duplicate(
    wall1,
    position=(0,1,100),
    scale=(200,5,0.5),
    color=color.brown
)
wall3=duplicate(
    wall2,
    rotation_y=90,
position=(100,1,0)
)
wall4=duplicate(
    wall2,
    rotation_y=180,
position=(0,1,-100))
wall5=duplicate(
    wall2,
    rotation_y=90,
position=(-100,1,0)
)
for i in range(64):
    Entity(model='cube', origin_y=-.5, scale=2, texture='barrier.jpg', texture_scale=(1,2),
        x=random.uniform(64,-64),
        z=random.uniform(-64,64) + 64,
        collider='box',
        scale_y = random.uniform(2,3.5) -0.5 or +0.5,
        color=color.hsv(0, 0, random.uniform(.9, 1))
        )
def update():
    if held_keys['left mouse']:
        shoot()
def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.3, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)
class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube',world_scale=(1,.1,.1), scale=1, origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp
    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5
    @property
    def hp(self):
        return self._hp
    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return
        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1
enemies = [Enemy(x=random.randrange(-7, -2)*random.randrange(2,9)) for x in range(20)]
enemies = [Enemy(z=random.randrange(-7, 2)*random.randrange(2,9)) for z in range(20)]
def pause_input(key):
    if key == 'tab':   
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled
pause_handler = Entity(ignore_paused=True, input=pause_input)
sun = DirectionalLight()
Sky()
app.run()
