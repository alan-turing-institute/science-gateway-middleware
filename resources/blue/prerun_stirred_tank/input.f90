!!!!!!!!!!!!!!!!!!!!!!!!!! -*- Mode: F90 -*- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! aeration.f90 --- aeration test
!! Auteur          : Jalel Chergui (LIMSI-CNRS) <Jalel.Chergui@limsi.fr>
!! Cree le         : Tue Sep 22 09:37:35 2009
!! Dern. mod. par  : Jalel Chergui (LIMSI-CNRS) <Jalel.Chergui@limsi.fr>
!! Dern. mod. le   : Sun Apr  1 22:23:36 2012
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module USER
  use BLUE

  implicit none
!!!!   TANK PARAMETERS
  real(kind=d), parameter :: TANK_RADIUS         =  0.5_d*0.085_d  !  (m)
  real(kind=d), parameter :: Interface_Level     =  0.07_d 
!!!!   IMPELLER PARAMETERS
  real(kind=d), parameter :: BLADE_RADIUS        =   0.0125_d    !  (m)
  real(kind=d), parameter :: BLADE_LENGTH        =   0.025_d    !  (m)
  real(kind=d), parameter :: BLADE_HEIGHT        =   0.01_d     !  (m)
  real(kind=d), parameter :: BLADE_WIDTH         =   0.002_d    !  (m)
  integer     , parameter :: BLADE_NUMBER        =   4
  real(kind=d), parameter :: BLADE_ANGLE         =   45.0_d     ! (Degree)
  real(kind=d), parameter :: Clearance           =   0.035     !  (m)
  real(kind=d), parameter :: DISK_RADIUS         =   0.005_d    !  (m)
  real(kind=d), parameter :: DISK_WIDTH          =   0.009_d    !  (m)
  real(kind=d), parameter :: TUBE_RADIUS         =   0.0025_d    !  (m)
  real(kind=d), parameter :: Impeller_Frequency  =   11.0_d
 

  public :: USER_solid, USER_interface, USER_bcd 

  contains
!***********************************************************************
  subroutine USER_interface(ini)
!***********************************************************************
    implicit none

    type(ini_3d), intent(inout) :: ini
    real(kind=d) :: x0, y0, z0

    x0 = 0.5_d*(BOX(1)+BOX(2))
    y0 = 0.5_d*(BOX(3)+BOX(4))
    z0 = BOX(5) + Interface_Level

    call INE_plane(INI=ini, BASEPOINT=[x0, y0, z0], ORIENTATION=[0.0_d, 0.0_d,-1.0_d])
    call INE_finalize(INI=ini)
  end subroutine USER_interface
!***********************************************************************
  function USER_solid(obj) result(distance)
!***********************************************************************
    implicit none

    ! Dummy
    type(obj_3d), intent(inout) :: obj
    real(kind=d)                :: distance
    ! Locals    
    integer :: i
    real   (kind=d) :: Theta, XX, YY, ZZ
    real   (kind=d) :: x0, y0, z0, angle 
    type(cylinder)  :: tank_c1
    type(block)     :: blade, blade0
    type(cylinder)  :: cyl1, cyl2
    type(plane)     :: pl1, pl2, pl3, tank_p1
    real(kind=d)    :: b0, b1, b, blades 
    real(kind=d)    :: c1, c2, p1, p2, p3, DISK, tank, TUBE_DISK

    x0 = 0.5_d*(BOX(1)+BOX(2))
    y0 = 0.5_d*(BOX(3)+BOX(4))
    z0 = Clearance
    angle = -BLADE_ANGLE * BLUE_PI_VALUE / 180.0_d
    

!    tank_c1 = cylinder(BASEPOINT=[x0,y0,z0], ORIENTATION=[0.0_d, 0.0_d, 1.0_d], RADIUS=TANK_RADIUS, INSIDE=FLUID)
!    tank_p1      = plane(BASEPOINT=[x0, y0, BOX(5)], ORIENTATION=[0.0_d, 0.0_d, 1.0_d])
!
!    c1   = tank_c1%distance(obj%subobj(0)%form)
!    p1   = tank_p1%distance(obj%subobj(0)%form)
!
!   tank = union(c1,p1)
!
!   obj%subobj(0)%distance = tank
!   obj%subobj(0)%movement = movement_property(FORCED=.TRUE., MOVING=.FALSE., TRANSLATION_VELOCITY=[0.0_d, 0.0_d, 0.0_d], & 
!    							    ROTATION_VELOCITY=[0.0_d, 0.0_d, 0.0_d])

!!! BLUID BLADES 
        Theta     = 0.0_d
        XX        = x0 + BLADE_RADIUS * cos(Theta)
        YY        = y0 + BLADE_RADIUS * sin(Theta)
        ZZ        = z0

      blade0       = block(EXTENT=[XX - 0.5_d*BLADE_LENGTH, XX + 0.5_d*BLADE_LENGTH,  &
                                   YY - 0.5_d*BLADE_WIDTH , YY + 0.5_d*BLADE_WIDTH ,  &
                                   ZZ - 0.5_d*BLADE_HEIGHT, ZZ + 0.5_d*BLADE_HEIGHT ],&
                                   ORIENTATION=[angle*cos(Theta), angle*sin(Theta), Theta ], INSIDE=SOLID)
      b0           =   blade0%distance(obj%form)

      do i = 1 , BLADE_NUMBER-1
        Theta     = real(i, kind=d) * 2.0_d * BLUE_PI_VALUE / real(BLADE_NUMBER, kind=d) 
        XX        = x0 + BLADE_RADIUS * cos(Theta)
        YY        = y0 + BLADE_RADIUS * sin(Theta)
        ZZ        = z0
 
        blade      = block(EXTENT=[XX - 0.5_d*BLADE_LENGTH, XX + 0.5_d*BLADE_LENGTH,  &
                                   YY - 0.5_d*BLADE_WIDTH , YY + 0.5_d*BLADE_WIDTH ,  &
                                   ZZ - 0.5_d*BLADE_HEIGHT, ZZ + 0.5_d*BLADE_HEIGHT ],&
                                   ORIENTATION=[angle*cos(Theta), angle*sin(Theta), abs(Theta) ], INSIDE=SOLID)
        b1= blade%distance(obj%form)
        b = union(b1,b0)
        b0= b
      end do      
      
      blades = b0
!!! BUILD DISK       
      cyl1 = cylinder(BASEPOINT=[x0 , y0, z0], ORIENTATION=[0.0_d, 0.0_d, 1.0_d], RADIUS=DISK_RADIUS, INSIDE=SOLID)
      pl1  = plane(BASEPOINT=[x0, y0, z0 - 0.5_d*DISK_WIDTH], ORIENTATION=[0.0_d, 0.0_d, -1.0_d])
      pl2  = plane(BASEPOINT=[x0, y0, z0 + 0.5_d*DISK_WIDTH], ORIENTATION=[0.0_d, 0.0_d, +1.0_d])
      cyl2 = cylinder(BASEPOINT=[x0 , y0, z0], ORIENTATION=[0.0_d, 0.0_d, 1.0_d], RADIUS=TUBE_RADIUS, INSIDE=SOLID)
      pl3  = plane(BASEPOINT=[x0, y0, 0.85_d*(BOX(5)+BOX(6))], ORIENTATION=[0.0_d, 0.0_d, +1.0_d])       
      
      c1 = cyl1%distance(obj%form)
      p1 = pl1%distance(obj%form)
      p2 = pl2%distance(obj%form)
      c2 = cyl2%distance(obj%form)
      p3 = pl3%distance(obj%form)
      DISK = intersection(intersection(c1,p1),p2)
      TUBE_DISK = intersection(intersection(intersection(union(c2,p2),c1),p1),p3)
      obj%distance = union(DISK, blades)
      obj%movement = movement_property(FORCED=.TRUE., MOVING=.TRUE., TRANSLATION_VELOCITY=[0.0_d, 0.0_d, 0.0_d], ROTATION_VELOCITY=[0.0_d, 0.0_d, 2.0_d*BLUE_PI_VALUE*Impeller_Frequency])


    ! Global object
!    distance = union(obj%subobj(0)%distance, obj%distance) 


  end function USER_solid

!***********************************************************************
  subroutine USER_bcd(com, msh, var)
!***********************************************************************
    implicit none

    class(com_3d), intent(in)    :: com
    type(msh_3d), intent(in)    :: msh
    type(var_3d), intent(inout) :: var

    ! Locals
    integer      :: i, j, k
    real(kind=d) :: r, x0, y0

    y0=0.5_d*(BOX(3)+BOX(4))
    x0=0.5_d*(BOX(1)+BOX(2))
!

       do k=msh%u%mem_kstart+1,msh%u%mem_kend-1
        do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
         do i=msh%u%mem_istart+1,msh%u%mem_iend-1
            r=sqrt((msh%p%y(j)-y0)**2+(msh%p%x(i)-x0)**2)
            if (r >= TANK_RADIUS)  var%u%fn(i,j,k) =  0.0_d
            if ((r <= TUBE_RADIUS) .and. (msh%p%z(k)<= 0.85_d*(BOX(6)+BOX(5))) .and. (msh%p%z(k) >= BOX(5) + Clearance) ) &
	        var%u%fn(i,j,k) = -2.0_d * BLUE_PI_VALUE * Impeller_Frequency * (msh%p%y(j)-y0) 
         enddo
        enddo
       enddo
       
       do k=msh%v%mem_kstart+1,msh%v%mem_kend-1
        do j=msh%v%mem_jstart+1,msh%v%mem_jend-1
         do i=msh%v%mem_istart+1,msh%v%mem_iend-1
            r=sqrt((msh%p%y(j)-y0)**2+(msh%p%x(i)-x0)**2)
            if (r >= TANK_RADIUS)  var%v%fn(i,j,k) =  0.0_d
            if ((r <= TUBE_RADIUS) .and. (msh%p%z(k)<= 0.85_d*(BOX(6)+BOX(5))) .and. (msh%p%z(k) >= BOX(5) + Clearance ) ) &
	        var%v%fn(i,j,k) = +2.0_d * BLUE_PI_VALUE * Impeller_Frequency * (msh%p%x(i)-x0)
         enddo
        enddo
       enddo

       do k=msh%w%mem_kstart+1,msh%w%mem_kend-1
        do j=msh%w%mem_jstart+1,msh%w%mem_jend-1
         do i=msh%w%mem_istart+1,msh%w%mem_iend-1
            r=sqrt((msh%p%y(j)-y0)**2+(msh%p%x(i)-x0)**2)
            if (r >= TANK_RADIUS)  var%w%fn(i,j,k) = 0.0_d
         enddo
        enddo
       enddo

!       do k=msh%h%mem_kstart+1,msh%h%mem_kend-1
!        do j=msh%h%mem_jstart+1,msh%h%mem_jend-1
!         do i=msh%h%mem_istart+1,msh%h%mem_iend-1
!            r=sqrt((msh%p%y(j)-y0)**2+(msh%p%x(i)-x0)**2)
!            if (r >= TANK_RADIUS)  var%h%bctype = "N"
!         enddo
!        enddo
!       enddo

 end subroutine USER_bcd

end module USER

program waves
  use USER

  implicit none

  type(com_3d)          :: com
  type(msh_3d)          :: msh
  type(sl_3d)          :: adv
  type(var_3d)          :: var
  type(gmres_mgmres_3d) :: solver
  type(BLUE_CLOCK)      :: clock
  integer               :: rfd
  integer               :: time_step_index, code

  ! Set MSH.
  call MSH_set(COM=com, MSH=msh)

  ! Set VAR.
  call VAR_set(COM=com, MSH=msh, VAR=var, SOLID_OBJECT=USER_solid, INITIAL_INTERFACE=USER_interface, BCD_METHOD = USER_bcd )

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
