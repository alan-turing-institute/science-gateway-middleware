!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -*- Mode: F90 -*- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! waves.f90 --- Moving object test
!! Auteur          : Damir Juric (LIMSI-CNRS) <Damir.Juric@limsi.fr>
!! Cree le         : Tue Sep 22 09:37:35 2009
!! Dern. mod. par  : Jalel Chergui (LIMSI-CNRS) <Jalel.Chergui@limsi.fr>
!! Dern. mod. le   : Sun Apr  1 22:23:36 2012
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module USER
  use BLUE

  implicit none
!   TANK PARAMETERS
  real(kind=d), parameter :: TANK_RADIUS           =  0.05_d     !  (m)
  real(kind=d), parameter :: BAFFLES_WIDTH         =  0.005_d    !  (m)
  real(kind=d), parameter :: BAFFLES_THICKNESS     =  0.001_d    !  (m)
!  IMPELLER PARAMETERS
  real(kind=d), parameter :: BLADE_RADIUS          =   0.0125_d  !  (m)
  real(kind=d), parameter :: BLADE_LENGTH          =   0.025_d   !  (m)
  real(kind=d), parameter :: BLADE_HEIGHT          =   0.01_d    !  (m)
  real(kind=d), parameter :: BLADE_WIDTH           =   0.002_d   !  (m)
  integer     , parameter :: BLADE_NUMBER          =   4
  real(kind=d), parameter :: BLADE_ANGLE           =   45.0_d    ! (Degree)
  real(kind=d), parameter :: Disk_Radius           =   0.005_d   !  (m)
  real(kind=d), parameter :: Disk_Width            =   0.009_d   !  (m)
  real(kind=d), parameter :: Tube_Radius           =   0.0025_d  !  (m)
  real(kind=d), parameter :: Clearance             =   0.050_d  !  (m)
  real(kind=d), parameter :: Rot_Frequency         =   5.0_d     !  (m)
  public :: USER_solid

  contains
!***********************************************************************
  function USER_solid(obj) result(distance)
!***********************************************************************
    implicit none

    ! Dummy
    type(obj_3d), intent(inout) :: obj
    real(kind=d)                :: distance
    ! Locals
    integer :: i
    real   (kind=d), dimension(BLADE_NUMBER) :: Theta_Impeller, XX, YY, ZZ, XX_IN, XX_OUT, YY_IN, YY_OUT, XX_LEFT, XX_RIGHT, YY_LEFT, YY_RIGHT
    real   (kind=d), dimension(BLADE_NUMBER) :: Z_TOP, Z_BOT

    real   (kind=d):: Theta_Impeller0, XX0, YY0, ZZ0, XX_IN0, XX_OUT0, YY_IN0, YY_OUT0, XX_LEFT0, XX_RIGHT0, YY_LEFT0, YY_RIGHT0
    real   (kind=d):: Theta_Baffle0, baffle_in0, baffle_left0, baffle_right0
    real   (kind=d)::   Z_TOP0, Z_BOT0
    real   (kind=d):: x0, y0, z0, angle_blade
    type(cylinder) :: tank_c
    type(plane)    :: Tank_ptop, Tank_pbot
    type(plane)    :: p1_east_west, p2_east_west, p3_east_west, p4_east_west
    type(plane)    :: p1_front_back, p2_front_back, p3_front_back, p4_front_back
    real(kind=d)   :: c, c1, c2, c3, c4, p1, p2, p3, p4, e1, tube_disk, baffle_front_back, baffle_east_west, tank
    type(cylinder) :: impeller_c1, impeller_c2
    type(plane)    :: impeller_p1, impeller_p2, impeller_p3
    type(plane)    :: blade_in, blade_out, blade_left, blade_right, blade_bot, blade_top
    type(plane)    :: blade0_in, blade0_out, blade0_left, blade0_right, blade0_bot, blade0_top
    real(kind=d)   :: bi, bo, bl, br, bb, bt, blade
    real(kind=d)   :: b0i, b0o, b0l, b0r, b0b, b0t, blade0, blade1
    x0=0.5_d*(BOX(1)+BOX(2))
    y0=0.5_d*(BOX(3)+BOX(4))
    z0= BOX(5) + Clearance
    angle_blade = -BLADE_ANGLE * BLUE_PI_VALUE / 180.0_d
    Theta_Baffle0 = 0.0_d
!
!
    tank_c    = cylinder(BASEPOINT=[x0,y0,z0], ORIENTATION=[0.0_d, 0.0_d, 1.0_d], RADIUS=TANK_RADIUS, INSIDE=FLUID)
    tank_ptop = plane(BASEPOINT=[x0, y0, BOX(6) - obj%msh%dz], ORIENTATION=[0.0_d, 0.0_d,-1.0_d])
    tank_pbot = plane(BASEPOINT=[x0, y0, BOX(5) + obj%msh%dz], ORIENTATION=[0.0_d, 0.0_d,+1.0_d])
    c  = tank_c%distance(obj%subobj(0)%form)
    p1 = tank_ptop%distance(obj%subobj(0)%form)
    p2 = tank_pbot%distance(obj%subobj(0)%form)
!    tank = union(union(c,p1),p2)
    tank = union(c,p2)

    p1_east_west = plane(BASEPOINT=[BOX(1) + BAFFLES_WIDTH , y0, z0], ORIENTATION=[+1.0_d, 0.0_d, 0.0_d])
    p2_east_west = plane(BASEPOINT=[BOX(2) - BAFFLES_WIDTH , y0, z0], ORIENTATION=[-1.0_d, 0.0_d, 0.0_d])
    p3_east_west = plane(BASEPOINT=[x0, y0 + 0.5_d*BAFFLES_THICKNESS, z0], ORIENTATION=[0.0_d, +1.0_d, 0.0_d])
    p4_east_west = plane(BASEPOINT=[x0, y0 - 0.5_d*BAFFLES_THICKNESS, z0], ORIENTATION=[0.0_d, -1.0_d, 0.0_d])

    p1 = p1_east_west%distance(obj%subobj(0)%form)
    p2 = p2_east_west%distance(obj%subobj(0)%form)
    p3 = p3_east_west%distance(obj%subobj(0)%form)
    p4 = p4_east_west%distance(obj%subobj(0)%form)
    baffle_east_west = intersection(intersection(union(p1,p2),p3),p4)

    p1_front_back = plane(BASEPOINT=[x0, BOX(3) +  BAFFLES_WIDTH  , z0], ORIENTATION=[0.0_d, +1.0_d, 0.0_d])
    p2_front_back = plane(BASEPOINT=[x0, BOX(4) -  BAFFLES_WIDTH  , z0], ORIENTATION=[0.0_d, -1.0_d, 0.0_d])
    p3_front_back = plane(BASEPOINT=[x0 + 0.5_d*BAFFLES_THICKNESS, y0, z0], ORIENTATION=[+1.0_d, 0.0_d, 0.0_d])
    p4_front_back = plane(BASEPOINT=[x0 - 0.5_d*BAFFLES_THICKNESS, y0, z0], ORIENTATION=[-1.0_d, 0.0_d, 0.0_d])

    p1 = p1_front_back%distance(obj%subobj(0)%form)
    p2 = p2_front_back%distance(obj%subobj(0)%form)
    p3 = p3_front_back%distance(obj%subobj(0)%form)
    p4 = p4_front_back%distance(obj%subobj(0)%form)
    baffle_front_back = intersection(intersection(union(p1,p2),p3),p4)


    ! subobj: 0


    obj%subobj(0)%distance = union(union(tank,baffle_east_west),baffle_front_back)


    ! subobj: 1
    impeller_c1 = cylinder(BASEPOINT=[x0,y0,z0], ORIENTATION=[0.0_d, 0.0_d, 1.0_d], RADIUS=Tube_Radius, INSIDE=SOLID)
    impeller_c2 = cylinder(BASEPOINT=[x0,y0,z0], ORIENTATION=[0.0_d, 0.0_d, 1.0_d], RADIUS=Disk_Radius, INSIDE=SOLID)
    impeller_p1 = plane(BASEPOINT=[x0, y0 , z0 + Disk_Width/2.0_d ], ORIENTATION=[0.0_d, 0.0_d, 1.0_d])
    impeller_p2 = plane(BASEPOINT=[x0, y0 , z0 - Disk_Width/2.0_d ], ORIENTATION=[0.0_d, 0.0_d, -1.0_d])
    impeller_p3 = plane(BASEPOINT=[x0, y0 , 0.75_d*(BOX(5)+BOX(6)) ], ORIENTATION=[0.0_d, 0.0_d, 1.0_d])
    c1 = impeller_c1%distance(obj%subobj(1)%form)
    c2 = impeller_c2%distance(obj%subobj(1)%form)
    p1 = impeller_p1%distance(obj%subobj(1)%form)
    p2 = impeller_p2%distance(obj%subobj(1)%form)
    p3 = impeller_p3%distance(obj%subobj(1)%form)

    tube_disk = intersection(intersection(intersection(union(c1,p1),c2),p2),p3)


      Theta_Impeller0    =    0.0_d
      XX0       = BLADE_RADIUS * cos(Theta_Impeller0) + x0
      YY0       = BLADE_RADIUS * sin(Theta_Impeller0) + y0
      ZZ0       = z0
      XX_OUT0   = (BLADE_RADIUS + BLADE_LENGTH/2.0_d)  * cos(Theta_Impeller0) + x0
      XX_IN0    = (BLADE_RADIUS - BLADE_LENGTH/2.0_d)  * cos(Theta_Impeller0) + x0
      YY_OUT0   = (BLADE_RADIUS + BLADE_LENGTH/2.0_d)  * sin(Theta_Impeller0) + y0
      YY_IN0    = (BLADE_RADIUS - BLADE_LENGTH/2.0_d)  * sin(Theta_Impeller0) + y0
      XX_LEFT0  =  XX0 - BLADE_WIDTH/2.0_d *sin(Theta_Impeller0) + BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))
      XX_RIGHT0 =  XX0 + BLADE_WIDTH/2.0_d *sin(Theta_Impeller0) - BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))
      YY_LEFT0  =  YY0 + BLADE_WIDTH/2.0_d *cos(Theta_Impeller0) + BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))
      YY_RIGHT0 =  YY0 - BLADE_WIDTH/2.0_d *cos(Theta_Impeller0) - BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))

      Z_TOP0     = ZZ0 + BLADE_HEIGHT/2.0_d / cos(angle_blade)
      Z_BOT0     = ZZ0 - BLADE_HEIGHT/2.0_d / cos(angle_blade)


      blade0_in    = plane(BASEPOINT=[XX_IN0   , YY_IN0   , z0], ORIENTATION=[-cos(Theta_Impeller0),-sin(Theta_Impeller0), 0.0_d])
      blade0_out   = plane(BASEPOINT=[XX_OUT0  , YY_OUT0  , z0], ORIENTATION=[+cos(Theta_Impeller0),+sin(Theta_Impeller0), 0.0_d])
      blade0_left  = plane(BASEPOINT=[XX_LEFT0 , YY_LEFT0 , z0 + BLADE_WIDTH/2.0_d*sin(angle_blade) ], ORIENTATION=[-sin(Theta_Impeller0)*cos(angle_blade),+cos(Theta_Impeller0)*cos(angle_blade), sin(angle_blade)])
      blade0_right = plane(BASEPOINT=[XX_RIGHT0, YY_RIGHT0, z0 - BLADE_WIDTH/2.0_d*sin(angle_blade)], ORIENTATION=[+sin(Theta_Impeller0)*cos(angle_blade),-cos(Theta_Impeller0)*cos(angle_blade), -sin(angle_blade)])
      blade0_top   = plane(BASEPOINT=[XX0, YY0, Z_TOP0], ORIENTATION=[sin(angle_blade)*sin(Theta_Impeller0),-sin(angle_blade)*cos(Theta_Impeller0), cos(angle_blade) ])
      blade0_bot   = plane(BASEPOINT=[XX0, YY0, Z_BOT0], ORIENTATION=[-sin(angle_blade)*sin(Theta_Impeller0), sin(angle_blade)*cos(Theta_Impeller0), -cos(angle_blade)])

      b0i= blade0_in%distance(obj%subobj(1)%form)
      b0o= blade0_out%distance(obj%subobj(1)%form)
      b0l= blade0_left%distance(obj%subobj(1)%form)
      b0r= blade0_right%distance(obj%subobj(1)%form)
      b0t= blade0_top%distance(obj%subobj(1)%form)
      b0b= blade0_bot%distance(obj%subobj(1)%form)

     blade0 = intersection(intersection(intersection(intersection(intersection(b0i,b0o),b0l), b0r), b0t), b0b)

    do i = 1 , BLADE_NUMBER

      Theta_Impeller(i) = (i-1) * 2.0_d * BLUE_PI_VALUE / BLADE_NUMBER
      XX       (i) = BLADE_RADIUS * cos(Theta_Impeller(i)) + x0
      YY       (i) = BLADE_RADIUS * sin(Theta_Impeller(i)) + y0
      ZZ       (i) = z0
      XX_OUT   (i) = (BLADE_RADIUS + BLADE_LENGTH/2.0_d)  * cos(Theta_Impeller(i)) + x0
      XX_IN    (i) = (BLADE_RADIUS - BLADE_LENGTH/2.0_d)  * cos(Theta_Impeller(i)) + x0
      YY_OUT   (i) = (BLADE_RADIUS + BLADE_LENGTH/2.0_d)  * sin(Theta_Impeller(i)) + y0
      YY_IN    (i) = (BLADE_RADIUS - BLADE_LENGTH/2.0_d)  * sin(Theta_Impeller(i)) + y0
      XX_LEFT  (i) =  XX(i) - BLADE_WIDTH/2.0_d *sin(Theta_Impeller(i)) + BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))
      XX_RIGHT (i) =  XX(i) + BLADE_WIDTH/2.0_d *sin(Theta_Impeller(i)) - BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))
      YY_LEFT  (i) =  YY(i) + BLADE_WIDTH/2.0_d *cos(Theta_Impeller(i)) + BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))
      YY_RIGHT (i) =  YY(i) - BLADE_WIDTH/2.0_d *cos(Theta_Impeller(i)) - BLADE_WIDTH/2.0_d * (1.0_d - cos(angle_blade))

      Z_TOP    (i) = ZZ(i) + BLADE_HEIGHT/2.0_d / cos(angle_blade)
      Z_BOT    (i) = ZZ(i) - BLADE_HEIGHT/2.0_d / cos(angle_blade)

      blade_in    = plane(BASEPOINT=[XX_IN(i)   , YY_IN(i)   , z0], ORIENTATION=[-cos(Theta_Impeller(i)),-sin(Theta_Impeller(i)), 0.0_d])
      blade_out   = plane(BASEPOINT=[XX_OUT(i)  , YY_OUT(i)  , z0], ORIENTATION=[+cos(Theta_Impeller(i)),+sin(Theta_Impeller(i)), 0.0_d])
      blade_left  = plane(BASEPOINT=[XX_LEFT(i) , YY_LEFT(i) , z0 + BLADE_WIDTH/2.0_d*sin(angle_blade) ], ORIENTATION=[-sin(Theta_Impeller(i))*cos(angle_blade),+cos(Theta_Impeller(i))*cos(angle_blade), sin(angle_blade)])
      blade_right = plane(BASEPOINT=[XX_RIGHT(i), YY_RIGHT(i), z0 - BLADE_WIDTH/2.0_d*sin(angle_blade)], ORIENTATION=[+sin(Theta_Impeller(i))*cos(angle_blade),-cos(Theta_Impeller(i))*cos(angle_blade), -sin(angle_blade)])
      blade_top   = plane(BASEPOINT=[XX(i), YY(i), Z_TOP(i)], ORIENTATION=[sin(angle_blade)*sin(Theta_Impeller(i)),-sin(angle_blade)*cos(Theta_Impeller(i)), cos(angle_blade) ])
      blade_bot   = plane(BASEPOINT=[XX(i), YY(i), Z_BOT(i)], ORIENTATION=[-sin(angle_blade)*sin(Theta_Impeller(i)), sin(angle_blade)*cos(Theta_Impeller(i)), -cos(angle_blade)])

      bi= blade_in%distance(obj%subobj(1)%form)
      bo= blade_out%distance(obj%subobj(1)%form)
      bl= blade_left%distance(obj%subobj(1)%form)
      br= blade_right%distance(obj%subobj(1)%form)
      bt= blade_top%distance(obj%subobj(1)%form)
      bb= blade_bot%distance(obj%subobj(1)%form)

      blade1 = intersection(intersection(intersection(intersection(intersection(bi,bo),bl), br), bt), bb)
      blade  = union(blade1, blade0)
      blade0 = blade
     end do

    obj%subobj(1)%distance = union(tube_disk,blade)  !intersection(intersection(union(c1,p1),c2),p2)
    obj%subobj(1)%movement = movement_property(FORCED=.TRUE., MOVING=.TRUE., TRANSLATION_VELOCITY=[0.0_d, 0.0_d, 0.0_d], ROTATION_VELOCITY=[0.0_d, 0.0_d, 2.0_d*BLUE_PI_VALUE*Rot_Frequency])

    ! Global object
    distance = union(obj%subobj(0)%distance, obj%subobj(1)%distance)
  end function USER_solid
end module USER

program waves
  use USER

  implicit none

  type(com_3d)          :: com
  type(msh_3d)          :: msh
  type(eno_3d)          :: adv
  type(var_3d)          :: var
  type(gmres_mgmres_3d) :: solver
  type(BLUE_CLOCK)      :: clock
  integer               :: rfd
  integer               :: time_step_index, code

  ! Set MSH.
  call MSH_set(COM=com, MSH=msh)

  ! Set VAR.
  call VAR_set(COM=com, MSH=msh, VAR=var, SOLID_OBJECT=USER_solid)

  ! Set. ADV.
  call ADV_set(COM=com, MSH=msh, ADV=adv)

  ! Set solvers & operators
  call SOL_set(COM=com, MSH=msh, VAR=var, SOL=solver)

  ! Read restart file
  call RST_read(COM=com, MSH=msh, ADV=adv, VAR=var, FD=rfd)

  ! Start time counter
  call CLOCK%start(LABEL="WAVES")

  TIMESTEP: do time_step_index = 1, NUM_TIME_STEP

    ! Solve Navier-Stokes equations.
     call BLUE_solve(COM=com, MSH=msh, ADV=adv, SOL=solver, VAR=var)

    ! Output results
    call IOF_output(COM=com, MSH=msh, VAR=var, SOL=solver)

    ! Write restart file.
    call RST_write(COM=com, MSH=msh, ADV=adv, VAR=var, FD=rfd)

    ! Exit from time loop if run time is reached
    if ( BLUE_MUST_QUIT ) exit TIMESTEP

  end do TIMESTEP

  ! Stop time counter
  call CLOCK%stop(LABEL="WAVES")

  ! Free datatype objects.
  call COM%free()
end program waves
