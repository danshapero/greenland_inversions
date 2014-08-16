        !------------------------------------------------------------------!
        FUNCTION MUIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,Temp,Flux,U
        INTEGER :: nodenumber

        Real(kind=dp) :: x,y,z,zb,zs
        Real(kind=dp) :: LinearInterp

        ! Some physical constants
        Real(kind=dp), parameter :: kappa=2.3, yr=3.15567d7, &
            & Am10=3.985d-13*yr*1d18, Ap10=1.916d3*yr*1d18, &
            & Qm10=6d4, Qp10=139d3, Ry=8.314
        Real(kind=dp), external :: zbIni, zsIni

        integer :: nx,ny
        integer :: i,j

        ! For now, assume constant surface temperature and basal heat flux
        ! throughout; in future, we should be getting these from data and
        ! using
        !   Temp = TempIni( Model, nodenumber, dumy )
        !   Flux = FluxIni( Model, nodenumber, dumy )
        Temp = -13.d0
        Flux = 0.066d0

        zs = zsIni( Model, nodenumber, dumy )

        ! position of current point
        x=Model % Nodes % x(nodenumber)
        y=Model % Nodes % y(nodenumber)
        z=Model % Nodes % z(nodenumber)

        ! Find the temperature at the current node
        Temp = min(Temp+Flux/kappa*(zs-z), 0.d0)

        ! Return the viscosity, keeping account of the change in parameters
        ! at -10C
        if ( Temp<=-10.d0 ) then
            U = (Am10*exp(-Qm10/(Ry*(Temp+273))))**(-1.d0/3)
        else
            U = (Ap10*exp(-Qp10/(Ry*(Temp+273))))**(-1.d0/3)
        endif


        Return
        End



        !------------------------------------------------------------------!
        FUNCTION zsIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp),allocatable :: dem(:,:),xx(:),yy(:)
        Real(kind=dp) :: x,y
        Real(kind=dp) :: LinearInterp

        integer :: nx,ny
        integer :: i,j

        character(len=16) :: glacier

        logical :: Firsttime=.true.

        SAVE dem,xx,yy,nx,ny
        SAVE Firsttime

        if (Firsttime) then
                Firsttime=.False.

                ! open file
                call get_environment_variable('glacier',glacier)
                open(10,file='dems/'//trim(glacier)//'/zsDEM.xy')
                Read(10,*) nx
                Read(10,*) ny
                allocate(xx(nx),yy(ny))
                Allocate(dem(nx,ny))
                Do i=1,nx
                   Do j=1,ny
                      read(10,*) xx(i),yy(j),dem(i,j)
                   End Do
                End do
                close(10)
        End if

        ! position current point
        x=Model % Nodes % x (nodenumber)
        y=Model % Nodes % y (nodenumber)

        U=LinearInterp(dem,xx,yy,nx,ny,x,y)

        Return 
        End



        !------------------------------------------------------------------!
        FUNCTION zbIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp),allocatable :: dem(:,:),xx(:),yy(:)
        Real(kind=dp) :: x,y
        Real(kind=dp) :: LinearInterp

        integer :: nx,ny
        integer :: i,j

        character(len=16) :: glacier

        logical :: Firsttime=.true.

        SAVE dem,xx,yy,nx,ny
        SAVE Firsttime

        if (Firsttime) then
                Firsttime=.False.

                ! open file
                call get_environment_variable('glacier',glacier)
                open(10,file='dems/'//trim(glacier)//'/zbDEM.xy')
                Read(10,*) nx
                Read(10,*) ny
                allocate(xx(nx),yy(ny))
                Allocate(dem(nx,ny))
                Do i=1,nx
                   Do j=1,ny
                      read(10,*) xx(i),yy(j),dem(i,j)
                   End Do
                End do
                close(10)
        End if

        ! position current point
        x=Model % Nodes % x (nodenumber)
        y=Model % Nodes % y (nodenumber)

        U=LinearInterp(dem,xx,yy,nx,ny,x,y)

        Return 
        End


        !------------------------------------------------------------------!
        include 'Interp.f90'                                               !
        !------------------------------------------------------------------!
