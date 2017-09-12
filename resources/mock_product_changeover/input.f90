!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -*- Mode: F89 -*- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! pco.f90 Product Change Over Problem for P&G
!! Auteur: Damir Juric (LIMSI-CNRS) <Damir.Juric@limsi.fr>
!! Cree le         : Mon Feb 06  14:21:00 2017
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module USER
  use BLUE
    
  implicit none

  real(kind=d), parameter :: PIPE_RADIUS = 0.025_d 
  real(kind=d), parameter :: Reynolds    = 1000.0_d              

                             
  public :: USER_int, USER_obj, USER_init, USER_bcd

  contains

!***********************************************************************
  subroutine USER_int(ini)
!***********************************************************************
    implicit none

    type(ini_3d), intent(inout) :: ini
    real(kind=d) :: ox, oy, oz

    ox=0.1_d
    oy=0.5_d*(BOX(3)+BOX(4))
    oz=0.5_d*(BOX(5)+BOX(6))

    call INE_plane(INI=ini, BASEPOINT=[ox,oy,oz], ORIENTATION=[1.0_d,0.0_d,0.0_d])
    call INE_finalize(INI=ini)
    end subroutine USER_int
!***********************************************************************
  subroutine USER_obj(obj)
!***********************************************************************
     implicit none
     type(obj_3d), intent(inout) :: obj
!
     ! Locals
     real(kind=d) :: ox, oy, oz
!
     ox=0.5_d*(BOX(1)+BOX(2)) 
     oy=0.5_d*(BOX(3)+BOX(4))
     oz=0.5_d*(BOX(5)+BOX(6))
     !
     call OBJ_cylinder(OBJ=obj, RADIUS=PIPE_RADIUS, BASEPOINT=[ox, oy, oz], ORIENTATION=[1.0_d, 0.0_d, 0.0_d], INSIDE=FLUID)
     call OBJ_union(OBJ=obj)

     
     call OBJ_finalize(OBJ=obj)
  end subroutine USER_obj
!***********************************************************************
  subroutine USER_init(com, msh, var)
!***********************************************************************
    implicit none

    class(com_3d), intent(in)   :: com
    type(msh_3d), intent(in)    :: msh
    type(var_3d), intent(inout) :: var

    ! Locals
    integer      :: i, j, k
    real(kind=d) :: Distance
    real(kind=d) :: r, y0, z0, Ug 

    y0=0.5_d*(BOX(3)+BOX(4))
    z0=0.5_d*(BOX(5)+BOX(6))
    Ug = Reynolds*viscosity_phase_1/(density_phase_1*2.0_d*PIPE_RADIUS) 


!	do k=msh%u%mem_kstart+1,msh%u%mem_kend-1
!          do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
!            do i=msh%u%mem_istart+1,msh%u%mem_iend-1
!		r=sqrt((msh%p%y(j)-y0)**2+(msh%p%z(k)-z0)**2)
!		if (r <= 2.0_d*PIPE_RADIUS) var%u%fn(i,j,k) = 2.0_d*Ug*(1.0_d-(r/PIPE_RADIUS)**2)
! 	    enddo
!          enddo
!        enddo

    var%v%fn(:,:,:) = 0.0_d
    var%w%fn(:,:,:) = 0.0_d

    if ( BLUE_WEST_SIDE ) then
       do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
         do k=msh%u%mem_kstart+1,msh%u%mem_kend-1
            if (var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d)) var%u%bctype(msh%u%istart+1,j,k)="D"
         enddo
       enddo
       do j=msh%v%mem_jstart+1,msh%v%mem_jend-1
         do k=msh%v%mem_kstart+1,msh%v%mem_kend-1
           if (var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d)) var%v%bctype(msh%v%istart,j,k)="D"
        enddo
       enddo
       do j=msh%w%mem_jstart+1,msh%w%mem_jend-1
         do k=msh%w%mem_kstart+1,msh%w%mem_kend-1
          if (var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d)) var%w%bctype(msh%w%istart,j,k)="D"
         enddo
       enddo
       do j=msh%p%mem_jstart+1,msh%p%mem_jend-1
         do k=msh%p%mem_kstart+1,msh%p%mem_kend-1
          if(var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d)) var%p%bctype(msh%p%istart,j,k)="N"
         enddo
       enddo
    end if
    if ( BLUE_EAST_SIDE ) then
       do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
         do k=msh%u%mem_kstart+1,msh%u%mem_kend-1
            if (var%p%obj%fn(msh%p%iend,j,k) >= EPSILON(1.0_d)) var%u%bctype(msh%u%iend-1,j,k)="N"
         enddo
       enddo
       do j=msh%v%mem_jstart+1,msh%v%mem_jend-1
         do k=msh%v%mem_kstart+1,msh%v%mem_kend-1
           if (var%p%obj%fn(msh%p%iend,j,k) >= EPSILON(1.0_d)) var%v%bctype(msh%v%iend,j,k)="N"
         enddo
       enddo
       do j=msh%w%mem_jstart+1,msh%w%mem_jend-1
         do k=msh%w%mem_kstart+1,msh%w%mem_kend-1
          if (var%p%obj%fn(msh%p%iend,j,k) >= EPSILON(1.0_d)) var%w%bctype(msh%w%iend,j,k)="N"
         enddo
       enddo
       do j=msh%p%mem_jstart+1,msh%p%mem_jend-1
         do k=msh%p%mem_kstart+1,msh%p%mem_kend-1
          if(var%p%obj%fn(msh%p%iend,j,k) >= EPSILON(1.0_d)) var%p%bctype(msh%p%iend,j,k)="N"
         enddo
       enddo
    end if

  end subroutine USER_init
!***********************************************************************
  subroutine USER_bcd(com, msh, var)
!***********************************************************************
    implicit none

    class(com_3d), intent(in)    :: com
    type(msh_3d), intent(in)    :: msh
    type(var_3d), intent(inout) :: var

    ! Locals
    integer      :: j, k
    real(kind=d) :: r, y0, z0, Ug 

    y0=0.5_d*(BOX(3)+BOX(4))
    z0=0.5_d*(BOX(5)+BOX(6))
    Ug = Reynolds*viscosity_phase_1/(density_phase_1*2.0_d*PIPE_RADIUS) 
!
    ! BC on WEST face
    if ( BLUE_WEST_SIDE ) then

       do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
         do k=msh%u%mem_kstart+1,msh%u%mem_kend-1
            r=sqrt((msh%p%y(j)-y0)**2+(msh%p%z(k)-z0)**2)
            if (var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d)) var%u%west(j,k) = 2.0_d*Ug*(1.0_d-(r/PIPE_RADIUS)**2) 
        enddo
      enddo
      do j=msh%v%mem_jstart+1,msh%v%mem_jend-1
        do k=msh%v%mem_kstart+1,msh%v%mem_kend-1
           if (var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d)) var%v%west(j,k)  = 0.0_d
        enddo
      enddo
      do j=msh%w%mem_jstart+1,msh%w%mem_jend-1
        do k=msh%w%mem_kstart+1,msh%w%mem_kend-1
          if (var%p%obj%fn(msh%p%istart,j,k) >= EPSILON(1.0_d))  var%w%west(j,k) = 0.0_d
        enddo
      enddo
    end if

  end subroutine USER_bcd
!***********************************************************************
!
!***********************************************************************
end module USER

program qinghua
  use USER

  implicit none

  type(com_3d)        :: com
  type(msh_3d)        :: msh
  type(sl_3d)        :: adv
  type(var_3d)        :: var
!  type(exp_mgmres_3d) :: solver
  type(gmres_mgmres_3d) :: solver
  type(BLUE_CLOCK)    :: clock
  integer             :: fd
  integer             :: time_step_index, code
  ! Set MSH.
  call MSH_set(COM=com, MSH=msh)

  ! Set VAR.
  call VAR_set(COM=com, MSH=msh, VAR=var, USER_METHOD=USER_init, OBJ_METHOD=USER_obj, INT_METHOD=USER_int,BCD_METHOD=USER_bcd)

  ! Set. ADV.
  call ADV_set(COM=com, MSH=msh, ADV=adv)

  ! Set solvers & operators
  call SOL_set(COM=com, MSH=msh, VAR=var, SOL=solver)

  ! Read restart file
  call RST_read(COM=com, MSH=msh, ADV=adv, VAR=var, FD=fd)

  ! Start time counter
  call clock%start(LABEL="QINGHUA")

  TIMESTEP: do time_step_index = 1, NUM_TIME_STEP

    ! Solve interface/momentum equations.
    call BLUE_solve(COM=com, MSH=msh, ADV=adv, SOL=solver, VAR=var, BCD_METHOD=USER_bcd)

    ! Output some infos on the screen.
    call IOF_output(COM=com, MSH=msh, VAR=var, SOL=solver)

    ! Write restart file.
    call RST_write(COM=com, MSH=msh, ADV=adv, VAR=var, FD=fd)

    ! Exit from time loop if run time is reached
    if ( BLUE_MUST_QUIT ) exit TIMESTEP

  end do TIMESTEP

  ! Stop time counter
  call clock%stop(LABEL="QINGHUA")

  ! Finalize
  call COM%free()
end program qinghua

