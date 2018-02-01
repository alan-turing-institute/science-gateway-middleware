!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -*- Mode: F89 -*- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! fb250.f90 Fabre, Suzanne test case No. 250
!! Auteur: Aditya Karnik (Imperial) <a.karnik06@imperial.ac.uk>
!! Cree le         : Wed Apr 26  14:21:00 2017
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module USER
  use BLUE
    
  implicit none

  real(kind=d), parameter :: ex_force_phase1 = 6.7_d    ! (Pa/m = Newton/m^3)
  real(kind=d), parameter :: ex_force_phase2 = 6.7_d    ! (Pa/m = Newton/m^3)
  real(kind=d), parameter :: INT_height      = 0.0315_d  ! (m)
  
  public :: USER_int, USER_force

  contains

!***********************************************************************
  subroutine USER_int(ini)
!***********************************************************************
    implicit none

    type(ini_3d), intent(inout) :: ini
    real(kind=d) :: ox, oy, oz

    ox=0.50_d*(BOX(1)+BOX(2))
    oy=0.50_d*(BOX(3)+BOX(4))
    oz=INT_height

    call INE_plane(INI=ini, BASEPOINT=[ox,oy,oz], ORIENTATION=[0.0_d,0.0_d,1.0_d])
    
    call INE_finalize(INI=ini)
    end subroutine USER_int
!***********************************************************************
  subroutine USER_force(com, msh, var)
!***********************************************************************
    implicit none

    class(com_3d), intent(in)   :: com
    type(msh_3d), intent(in)    :: msh
    type(var_3d), intent(inout) :: var

    real(kind=d) :: acceleration_phase1, acceleration_phase2, func
    
!    func = 0.5 - atan(8.75*(2.5-BLUE_TIME))/BLUE_PI_VALUE;
    func = 1.;

!    print *,func

    acceleration_phase1 = (func*ex_force_phase1) / density_phase_1
    acceleration_phase2 = (func*ex_force_phase2) / density_phase_2

    var%u%fe(:,:,:) = acceleration_phase1 + (acceleration_phase2 - acceleration_phase1)*var%h%ohv(:,:,:)

  end subroutine USER_force
  !***********************************************************************

  !***********************************************************************
  subroutine USER_init(com, msh, var)
!***********************************************************************
    implicit none

    class(com_3d), intent(in)    :: com
    type(msh_3d),  intent(in)    :: msh
    type(var_3d),  intent(inout) :: var

!    ! Locals
    integer :: i, j, k, npts,isw,isw1,isw2,ipts,nypts
    real(kind=d), parameter :: ustarG = 0.33_d
    real(kind=d), parameter :: ustarI = 0.47_d
    real(kind=d), parameter :: ustarL = 0.0285_d
    real(kind=d), parameter :: nug = 1.56e-5_d
    real(kind=d), parameter :: nul = 8.91e-7_d
    real(kind=d) :: h,dz,zloc,yp,hi,vtemp,kc,yh,Ufit,len,ystarG,ystarI,ystarL,umag
    real(kind=d) :: fluxg,fluxl,yloc,w,kj,dy,rmag
    
    ystarG = nug/ustarG
    ystarI = nug/ustarI
    ystarL = nul/ustarL
    
    var%u%fn(:,:,:)=0.0_d
    var%w%fn(:,:,:)=0.0_d
    var%v%fn(:,:,:)=0.0_d

    len = BOX(2)-BOX(1)
    h = BOX(6)-BOX(5)
    w = BOX(4)-BOX(3)
    
    npts = msh%p%kend - 2
    dz = h/npts

    nypts = msh%p%jend - 2
    dy = w/nypts
    
    hi = INT_height

    isw = 0
    isw1 = 0
    isw2 = 0

    ipts = 0

    fluxg = 0
    fluxl = 0
    
    do k=msh%u%mem_kend-1,msh%u%mem_kstart+1,-1
       zloc = h - msh%p%z(k)

       if(zloc > 0) then
       if (zloc < (h-hi) ) then
          
          yp = (h-hi)/2
          if (zloc < yp) then
             ipts = ipts+1
             umag = max( (((log(zloc/ystarG) / 0.4) + 5.5) * ustarG), 0.0_d)            

             kj = (umag/ustarG) - (log((w/2.0_d)/ystarG) / 0.4)     
             do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
                yloc = msh%p%y(j)
                if(yloc>0)then
                   if(yloc<=(w/2.0_d))then
                      rmag = ((log(yloc/ystarG) / 0.4) + kj) * ustarG;
                      var%u%fn(:,j,k) = rmag
                      fluxg = fluxg + (dz*dy*rmag)
                   else
                      if(yloc<w)then
                         rmag = ((log((w-yloc)/ystarG) / 0.4) + kj) * ustarG;
                         var%u%fn(:,j,k) = rmag
                         fluxg = fluxg + (dz*dy*rmag)
                      end if
                   end if
                end if
             end do            
          else
             isw=isw+1
             if(isw==1) then
                vtemp = ((log((zloc-dz)/ystarG) / 0.4) + 5.5) * ustarG         
                kc = (vtemp/ustarI) - (log((h-hi-zloc)/ystarI) / 0.4)        
             end if
             ipts = ipts+1
             umag = max( (((log((h-hi-zloc)/ystarI) / 0.4) + kc) * ustarI), 0.0_d)
             kj = (umag/ustarG) - (log((w/2.0_d)/ystarG) / 0.4)     
             do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
                yloc = msh%p%y(j)
                if(yloc>0)then
                   if(yloc<=(w/2.0_d))then
                      rmag = ((log(yloc/ystarG) / 0.4) + kj) * ustarG;
                      var%u%fn(:,j,k) = rmag
                      fluxg = fluxg + (dz*dy*rmag)
                   else
                      if(yloc<w)then
                         rmag = ((log((w-yloc)/ystarG) / 0.4) + kj) * ustarG;
                         var%u%fn(:,j,k) = rmag
                         fluxg = fluxg + (dz*dy*rmag)
                      end if
                   end if
                end if
             end do   
          end if
       else
          yp = 0.6*hi
          if( zloc < (h-yp) ) then   
             yh = (h-zloc)/hi
             isw1=isw1+1
             if (isw1 == 1) then               
                vtemp = ((log((h-hi-(zloc-dz))/ystarI) / 0.4) + kc) * ustarI
                Ufit = vtemp / (yh-(0.39*(sin(BLUE_PI_VALUE*(1-yh)))))
             end if
             ipts = ipts+1
             umag = max( (Ufit * (yh-(0.39*(sin(BLUE_PI_VALUE*(1-yh)))))), 0.0_d)
             kj = (umag/ustarL) - (log((w/2.0_d)/ystarL) / 0.4)     
             do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
                yloc = msh%p%y(j)
                if(yloc>0)then
                   if(yloc<=(w/2.0_d))then
                      rmag = ((log(yloc/ystarL) / 0.4) + kj) * ustarL;
                      var%u%fn(:,j,k) = rmag
                      fluxl = fluxl + (dz*dy*rmag)
                   else
                      if(yloc<w)then
                         rmag = ((log((w-yloc)/ystarL) / 0.4) + kj) * ustarL;
                         var%u%fn(:,j,k) = rmag
                         fluxl = fluxl + (dz*dy*rmag)
                      end if
                   end if
                end if
             end do  
          else
             isw2=isw2+1
            if (isw2 == 1) then
                yh = (h-(zloc-dz))/hi
                vtemp = Ufit * (yh-(0.39*(sin(BLUE_PI_VALUE*(1-yh)))))
                kc = (vtemp/ustarL) - (log((h-zloc)/ystarL) / 0.4)
             end if
             if(zloc < h) then
                 ipts = ipts+1
                 umag = max( (((log((h-zloc)/ystarL) / 0.4) + kc) * ustarL), 0.0_d)
                 kj = (umag/ustarL) - (log((w/2.0_d)/ystarL) / 0.4)     
             do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
                yloc = msh%p%y(j)
                if(yloc>0)then
                   if(yloc<=(w/2.0_d))then
                      rmag = ((log(yloc/ystarL) / 0.4) + kj) * ustarL;
                      var%u%fn(:,j,k) = rmag
                      fluxl = fluxl + (dz*dy*rmag)
                   else
                      if(yloc<w)then
                         rmag = ((log((w-yloc)/ystarL) / 0.4) + kj) * ustarL;
                         var%u%fn(:,j,k) = rmag
                         fluxl = fluxl + (dz*dy*rmag)
                      end if
                   end if
                end if
             end do  
                end if
          end if
       end if
       end if
    end do

!print *,"FLUX ",fluxg,fluxl
!!$ do i=msh%u%mem_istart+1,msh%u%mem_iend-1
!!$    do j=msh%u%mem_jstart+1,msh%u%mem_jend-1
!!$       do k=msh%u%mem_kend-1,msh%u%mem_kstart+1,-1
!!$
!!$          zloc = msh%p%z(k)
!!$          
!!$          if (zloc < INT_height) then
!!$             var%u%fn(i,j,k) = 0.4
!!$          else
!!$             var%u%fn(i,j,k) = 4.5
!!$          end if
!!$
!!$       end do
!!$    end do
!!$ end do

    var%w%fn(:,:,:)=0.0_d
    var%v%fn(:,:,:)=0.0_d 
    
  end subroutine USER_init
  !***********************************************************************

  !***********************************************************************
  subroutine USER_les(msh, var)
!***********************************************************************
    implicit none

    type(msh_3d), intent(in)    :: msh
    type(var_3d), intent(inout) :: var

    integer :: k
    real(kind=d) :: zloc

    do k=msh%p%kend-1,msh%p%kstart+1,-1
       zloc = msh%p%z(k)
          if (zloc < INT_height) then
             var%p%mu(:,:,k) = 0.04045_d
          else
             var%p%mu(:,:,k) = 1.85e-5_d
          end if
    end do
    
  end subroutine USER_les
  
end module USER

program qinghua
  use USER

  implicit none

  type(com_3d)        :: com
  type(msh_3d)        :: msh
  type(eno_3d)        :: adv
  type(var_3d)        :: var
!  type(exp_mgmres_3d) :: solver
  type(gmres_mgmres_3d) :: solver
  type(BLUE_CLOCK)    :: clock
  integer             :: fd
  integer             :: time_step_index, code

  ! Set MSH.
  call MSH_set(COM=com, MSH=msh)

  ! Set VAR.
  call VAR_set(COM=com, MSH=msh, VAR=var, INITIAL_METHOD=USER_init, FORCE_METHOD=USER_force, INITIAL_INTERFACE=USER_int,LES_METHOD=USER_les)

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
    call BLUE_solve(COM=com, MSH=msh, ADV=adv, SOL=solver, VAR=var)

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

