from panda3d.core import *
loadPrcFileData("", "prefer-parasite-buffer #f")
import direct.directbase.DirectStart

# setup scene
scene = loader.loadModel('environment')
scene.reparentTo(render)
panda = loader.loadModel('panda')
panda.reparentTo(render)
panda.setY(30)
#panda.setShaderAuto(BitMask32.allOn() & ~BitMask32.bit(Shader.BitAutoShaderShadow))

# setup lights, shadow
light = render.attachNewNode(Spotlight("Spot"))
light.node().setScene(render)
render.setLight(light)
light.setP(-45)
light.setZ(20)
light.node().setShadowCaster(True)
light.node().setAttenuation(Point3(0,0,0))
light.node().showFrustum()
light.node().getLens().setFov(70)
light.node().getLens().setNearFar(10, 500)
light.node().getLens().setFilmSize(100, 100)

# the light which is actually used
dlight = render.attachNewNode(DirectionalLight("Directional"))
dlight.node().setScene(render)
render.setLight(dlight)

alight = render.attachNewNode(AmbientLight("Ambient"))
alight.node().setColor(Vec4(0.2, 0.2, 0.2, 1))
render.setLight(alight)

render.setShaderAuto()
run() 
