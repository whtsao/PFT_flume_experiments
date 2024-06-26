import numpy as np
import math
from proteus import Domain, Context
from proteus.mprans import SpatialTools as st
from scipy.spatial.distance import cdist
import proteus.TwoPhaseFlow.TwoPhaseFlowProblem as TpFlow
from proteus import WaveTools as wt

opts= Context.Options([
    ('ns_model',1,"ns_model={0,1} for {rans2p,rans3p}"),
    ("final_time",30.0,"Final time for simulation"),
    ("sampleRate",0.5,"Time interval to output solution"),
    ("gauges", True, "Collect data for validation"),
    ("cfl",0.9,"Desired CFL restriction"),
    ("he",0.04,"Max mesh element diameter"),
    ("mwl",0.2,"still water depth"),
    ("Hm",0.1,"Wave height"),
    ("Tp",1.5,"Peak wave period"),
    ("wave_type",'Monochromatic',"runs simulation with time series waves"),
    ("filename",'test.csv',"name for csv file"),
    ("embed_structure",False,"Embed structure using a signed distance function"),
    ("density",'LD',"Change density of embedded forest")
    ])


# general options
# sim time
T = opts.final_time
# initial step
dt_init = 0.001
# CFL value
cfl = 0.5
# mesh size
he = opts.he
# rate at which values are recorded
sampleRate = opts.sampleRate

# physical options
# water density
rho_0 = 998.2
# water kinematic viscosity
nu_0 = 1.004e-6
# air density
rho_1 = 1.205
# air kinematic viscosity
nu_1 = 1.5e-5
# gravitational acceleration
g = np.array([0., 0., -9.81,])


# wave options
water_level = opts.mwl
wave_period = opts.Tp
wave_height = opts.Hm
wave_direction = np.array([1., 0., 0.])

#Monochromatic or Random
if opts.wave_type=='Monochromatic':
    wave = wt.MonochromaticWaves(period=wave_period,
                                 waveHeight=wave_height,
                                 mwl=water_level,
                                 depth=water_level,
                                 g=g,waveDir=wave_direction,
                                 waveType='Linear',Nf=8)

elif opts.wave_type=='Time':
    wave = wt.TimeSeries(timeSeriesFile=opts.filename, # e.g.= "Timeseries.txt",
                         skiprows=0,
                         timeSeriesPosition=np.array([0.62,0.,0.]),
                         depth=water_level,
                         N=100,          #number of frequency bins
                         mwl=water_level,        #mean water level
                         waveDir=wave_direction,
                         g=g,
                         cutoffTotal = 0.01,
                         rec_direct = True,
                         window_params = None)
    
else:
    wave = wt.RandomWaves(Tp=wave_period,
                          Hs=wave_height,
                          mwl=water_level,depth=water_level,
                          g=g,waveDir=wave_direction,
                          spectName='JONSWAP',N=300,bandFactor=2.5)


wavelength = wave.wavelength



#  ____                        _
# |  _ \  ___  _ __ ___   __ _(_)_ __
# | | | |/ _ \| '_ ` _ \ / _` | | '_ \
# | |_| | (_) | | | | | | (_| | | | | |
# |____/ \___/|_| |_| |_|\__,_|_|_| |_|
# Domain
# All geometrical options go here (but not mesh options)
domain = Domain.PiecewiseLinearComplexDomain()


# ----- SHAPES ----- #

# ----- TANK ----- #

boundaryOrientations = {'y-': np.array([0., -1.,0.]),
                        'x+': np.array([+1., 0.,0.]),
                        'y+': np.array([0., +1.,0.]),
                        'x-': np.array([-1., 0.,0.]),
                        'z+': np.array([0., 0.,+1.]),
                        'z-': np.array([0., 0.,-1.]),
                        'sponge': np.array([+1., 0.,0.]),
                           }

boundaryTags = {'y-' : 1,
                'x+' : 2,
                'y+' : 3,
                'x-' : 4,
                'z+' : 5,
                'z-' : 6,
                'sponge':7,
               }

slope1=0.35
zmax=0.45

top = 1.0

vertices=[[0.0,0.0,0.0],#0
         [2.5,0.0,0.0],#1                                                                      
         [4.1, 0.0,0.0], #2
         [4.9, 0.0,0.0],#3                                                                 
         [6.08, 0.0,slope1],#4                                                              
         [6.08, 0.0,zmax],#5                                                          
         [0.0, 0.0,zmax],#6                                                              
         [-wavelength,0.0,zmax],#7
         [-wavelength,0.0,0.0],#8
          
         [0.0,0.3,0.0],#9
         [2.5,0.3,0.0],#10                                                                      
         [4.1, 0.3,0.0], #11
         [4.9, 0.3,0.0],#12                                                                 
         [6.08, 0.3,slope1],#13                                                              
         [6.08, 0.3,zmax],#14                                                            
         [0.0, 0.3,zmax],#15                                                              
         [-wavelength,0.3,zmax],#16
         [-wavelength,0.3,0.0],]#17
          
    
vertexFlags=np.array([6, 6, 6, 6, 6, 6, 
                      5,
                      4, 4,
                      6, 6, 6, 6, 6, 6,                     
                      5,
                      4, 4,])

    
    
facets=[[[0,1,2,3,4,5,6]],#right                                    
        [[9,10,11,12,13,14,15]],#left                           
        [[6,5,14,15]],#top                                               
        [[0,1,10,9]],#bottom                                                         
        [[1,2,11,10]],
        [[2,3,12,11]],
        [[3,4,13,12]],
        [[4,5,14,13]],#back                                                           
        [[7,8,17,16]],#inflow--internal if sponge layer, switched to zero for internal
        [[0,9,15,6]], #sponge
        [[8,0,6,7]],
        [[8,0,9,17]],
        [[9,17,16,15]],
        [[6,15,16,7]],]
        
facetFlags=np.array([6,6,# right and left
                     5,#top
                     6,6,6,6,#bottom
                     6,#back
                     0,#inflow/internal
                     7,#sponge
                     6,6,6,5,])
                  
    
regions = [[ 0.1, 0.1,0.1],
           [-0.1, 0.1,0.1],]
    
regionFlags=np.array([1,2])

# TANK

tank = st.CustomShape(domain, vertices=vertices, vertexFlags=vertexFlags,
                      facets=facets, facetFlags=facetFlags,
                      regions=regions, regionFlags=regionFlags,
                      boundaryTags=boundaryTags, boundaryOrientations=boundaryOrientations)


# SPONGE LAYERS
# generation zone: 1 wavelength
# absorption zone: 2 wavelengths
#tank.setSponge(x_n=wavelength, x_p=2*wavelength)


#  ____                        _                   ____                _ _ _   _
# | __ )  ___  _   _ _ __   __| | __ _ _ __ _   _ / ___|___  _ __   __| (_) |_(_) ___  _ __  ___
# |  _ \ / _ \| | | | '_ \ / _` |/ _` | '__| | | | |   / _ \| '_ \ / _` | | __| |/ _ \| '_ \/ __|
# | |_) | (_) | |_| | | | | (_| | (_| | |  | |_| | |__| (_) | | | | (_| | | |_| | (_) | | | \__ \
# |____/ \___/ \__,_|_| |_|\__,_|\__,_|_|   \__, |\____\___/|_| |_|\__,_|_|\__|_|\___/|_| |_|___/
#                                           |___/
# Boundary Conditions

# TANK

# atmosphere on top
tank.BC['z+'].setAtmosphere()
# free slip on bottom
tank.BC['z-'].setFreeSlip()
# free slip on the right
tank.BC['x+'].setFreeSlip()
tank.BC['y-'].setFreeSlip()
# free slip on the right
tank.BC['y+'].setFreeSlip()

# non material boundaries for sponge interface
tank.BC['sponge'].setNonMaterial()

# WAVE AND RELAXATION ZONES

smoothing = he*1.5
dragAlpha = 5*2*np.pi/wave_period/(1.004e-6)
tank.BC['x-'].setUnsteadyTwoPhaseVelocityInlet(wave,
                                               smoothing=smoothing,
                                               vert_axis=1)

tank.setGenerationZones(flags=2,
                   epsFact_porous=wavelength*0.5,
                   center=[-wavelength*0.5,0.,zmax*0.5],
                   orientation=[1,0,0],
                   waves=wave,
                   dragAlpha=dragAlpha,
                   vert_axis=1,
                   porosity=1.,
                   smoothing=smoothing)

   
column_gauge_locations=[((1.35,0.15,0.),(1.35,0.15,zmax)),
			((2.49,0.15,0.),(2.49,0.15,zmax)),
			((4.19, 0.15,0.),(4.19,0.15,zmax))]


tank.attachLineIntegralGauges('vof',gauges=((('vof',), column_gauge_locations),),fileName='column_gauges.csv') 

#pressure_gauge_locations= ((1.43, 0.15, 0.07), (1.75, 0.15, 0.07),(2.07,0.15,0.07),(2.39,0.15,0.07))
#tank.attachPointGauges('twp', gauges=((('p',), pressure_gauge_locations),), fileName='pressure_gaugeArray.csv')

#velocity_gauge_locations=((32.24, -1.4,1.25), (43.09, -1.43, 1.40),(43.09,-1.43,1.55),(43.09,-1.43,1.72),(43.09,-1.43,1.86),(57.83,-1.41,1.38))
#tank.attachPointGauges('twp', gauges=((('u','v','w'), velocity_gauge_locations),), fileName='velocity_gaugeArray.csv')

    
#  ___       _ _   _       _    ____                _ _ _   _
# |_ _|_ __ (_) |_(_) __ _| |  / ___|___  _ __   __| (_) |_(_) ___  _ __  ___
#  | || '_ \| | __| |/ _` | | | |   / _ \| '_ \ / _` | | __| |/ _ \| '_ \/ __|
#  | || | | | | |_| | (_| | | | |__| (_) | | | | (_| | | |_| | (_) | | | \__ \
# |___|_| |_|_|\__|_|\__,_|_|  \____\___/|_| |_|\__,_|_|\__|_|\___/|_| |_|___/
# Initial Conditions

from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.ctransportCoefficients import smoothedHeaviside_integral
smoothing = 1.5*he
nd = 3

class zero(object):
    def uOfXT(self,x,t):
        return 0.0

class P_IC:
    def uOfXT(self, x, t):
        p_L = 0.0
        phi_L = zmax - water_level
        phi = x[2] - water_level
        p = p_L -g[2]*(rho_0*(phi_L - phi)
                          +(rho_1 -rho_0)*(smoothedHeaviside_integral(smoothing,phi_L)
                                                -smoothedHeaviside_integral(smoothing,phi)))
        return p
class U_IC:
    def uOfXT(self, x, t):
        return 0.0
class V_IC:
    def uOfXT(self, x, t):
        return 0.0
class W_IC:
    def uOfXT(self, x, t):
        return 0.0
class VF_IC:
    def uOfXT(self, x, t):
        return smoothedHeaviside(smoothing, x[2]-water_level)
class PHI_IC:
    def uOfXT(self, x, t):
        return x[2] - water_level

# instanciating the classes for *_p.py files
initialConditions = {'pressure': P_IC(),
                     'vel_u': U_IC(),
                     'vel_v': V_IC(),
                     'vel_w': W_IC(),
                     'vof': VF_IC(),
                     'ncls': PHI_IC(),
                     'rdls': PHI_IC()}

#  __  __           _        ___        _   _
# |  \/  | ___  ___| |__    / _ \ _ __ | |_(_) ___  _ __  ___
# | |\/| |/ _ \/ __| '_ \  | | | | '_ \| __| |/ _ \| '_ \/ __|
# | |  | |  __/\__ \ | | | | |_| | |_) | |_| | (_) | | | \__ \
# |_|  |_|\___||___/_| |_|  \___/| .__/ \__|_|\___/|_| |_|___/
#                                |_|

domain.MeshOptions.setParallelPartitioningType('node')
domain.boundaryTags = boundaryTags
he = opts.he
domain.MeshOptions.he = he
st.assembleDomain(domain)
domain.MeshOptions.triangleOptions="VApq1.25q12feena%e" % ((he**3)/6.0,)
domain.writePLY("mesh")
domain.writePoly("mesh")
domain.writeAsymptote("mesh")




#  _   _                           _
# | \ | |_   _ _ __ ___   ___ _ __(_) ___ ___
# |  \| | | | | '_ ` _ \ / _ \ '__| |/ __/ __|
# | |\  | |_| | | | | | |  __/ |  | | (__\__ \
# |_| \_|\__,_|_| |_| |_|\___|_|  |_|\___|___/
# Numerics

outputStepping = TpFlow.OutputStepping()
outputStepping.final_time=T
outputStepping.dt_init=dt_init
outputStepping.dt_output=sampleRate
outputStepping.nDTout=None

myTpFlowProblem = TpFlow.TwoPhaseFlowProblem()
myTpFlowProblem.domain=domain
myTpFlowProblem.SystemPhysics.initialConditions=initialConditions
myTpFlowProblem.outputStepping=outputStepping



myTpFlowProblem.SystemNumerics.cfl=0.33
myTpFlowProblem.SystemNumerics.useSuperlu=True

myTpFlowProblem.SystemPhysics.setDefaults()
myTpFlowProblem.SystemPhysics.useDefaultModels()
myTpFlowProblem.SystemPhysics.gravity = np.array([0.0,0.0,-9.8])

m = myTpFlowProblem.SystemPhysics.modelDict
# ADD RELAXATION ZONES TO AUXILIARY VARIABLES


m['flow'].p.initialConditions['p'] = P_IC()
m['flow'].p.initialConditions['u'] = zero()
m['flow'].p.initialConditions['v'] = zero()
m['flow'].p.initialConditions['w'] = zero()
m['vof'].p.initialConditions['vof'] = VF_IC()
m['ncls'].p.initialConditions['phi'] = PHI_IC()
m['rdls'].p.initialConditions['phid'] = PHI_IC()
m['mcorr'].p.initialConditions['phiCorr'] = zero()

m['flow'].auxiliaryVariables = domain.auxiliaryVariables['twp']
m['vof'].auxiliaryVariables = domain.auxiliaryVariables['vof']

# Add immersed solid

if opts.embed_structure:
        
    def particle_sdf(t, x):
        if opts.density=='HD':
            #HD Case
            x_c=[2.76,3.04,3.32,3.6,3.88,2.76,3.04,3.32,3.6,3.88,2.62,2.9,3.18,3.46,3.74,4.02]
            y_c=[0.0625,0.0625,0.0625,0.0625,0.0625,0.2375,0.2375,0.2375,0.2375,0.2375,0.15,0.15,0.15,0.15,0.15,0.15]
            r=[0.04445,0.04445,0.04445,0.04445,0.04445,0.04445,0.04445,0.04445,0.04445,0.04445,0.05715,0.05715,0.05715,0.05715,0.05715,0.05715]
        
        elif opts.density=='LD':
            #LD Case
            x_c=[2.76,3.32,3.88,3.04,3.6,2.62,3.18,3.74]
            y_c=[0.0625,0.0625,0.0625,0.2375,0.2375,0.15,0.15,0.15]
            r=[0.04445,0.04445,0.04445,0.04445,0.04445,0.05715,0.05715,0.05715]
        
        phi_final=10000
        for i in range(len(x_c)):
                dist = math.sqrt((x_c[i] - x[0])**2 + (y_c[i] - x[1])**2)
                x_normal=(x[0]-x_c[i])/dist
                y_normal=(x[1]-y_c[i])/dist
                phi=dist-r[i]
                if phi < phi_final:
                    phi_final = phi
                    normals=(x_normal, y_normal, 0.0)
        return phi_final, np.array(normals)

    def particle_vel(t, x):
        return (0.0,0.0,0.0)

    m['flow'].p.coefficients.particle_sdfList = [particle_sdf]
    m['flow'].p.coefficients.particle_velocityList = [particle_vel]
    m['flow'].p.coefficients.use_ball_as_particle=0
    m['flow'].p.coefficients.nParticles=1
    m['flow'].p.coefficients.useExact=True
    m['flow'].p.coefficients.particle_netForces = np.zeros((3*m['flow'].p.coefficients.nParticles, 3), 'd')
    m['flow'].p.coefficients.particle_netMoments = np.zeros((m['flow'].p.coefficients.nParticles, 3), 'd')
    m['flow'].p.coefficients.particle_surfaceArea = np.zeros((m['flow'].p.coefficients.nParticles,), 'd')
