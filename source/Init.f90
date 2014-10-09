        !------------------------------------------------------------------!
        FUNCTION USIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy, U
        INTEGER :: nodenumber

        Real(kind=dp), allocatable :: dem(:,:), xx(:), yy(:)
        Real(kind=dp) :: x, y
        Real(kind=dp) :: LinearInterp

        integer :: nx, ny
        integer :: i, j

        character(len=16) :: glacier

        logical :: Firsttime = .true.

        SAVE dem, xx, yy, nx, ny
        SAVE Firsttime

        if (Firsttime) then

                Firsttime = .False.

                call get_environment_variable('glacier', glacier)

                ! open file
                open(10,file='dems/' // trim(glacier) // '/UDEM.xy')
                Read(10,*) nx
                Read(10,*) ny
                allocate(xx(nx), yy(ny))
                Allocate(dem(nx, ny))
                Do i = 1, nx
                   Do j = 1, ny
                      read(10,*) xx(i), yy(j), dem(i,j)
                   End Do
                End do
                close(10)
        End if

        ! position current point
        x = Model % Nodes % x (nodenumber)
        y = Model % Nodes % y (nodenumber)

        U = LinearInterp(dem, xx, yy, nx, ny, x, y)

        Return 
        End



        !------------------------------------------------------------------!
        FUNCTION VSIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy, U
        INTEGER :: nodenumber

        Real(kind=dp), allocatable :: dem(:,:), xx(:), yy(:)
        Real(kind=dp) :: x, y
        Real(kind=dp) :: LinearInterp

        integer :: nx, ny
        integer :: i, j

        character(len=16) :: glacier

        logical :: Firsttime = .true.

        SAVE dem, xx, yy, nx, ny
        SAVE Firsttime

        if (Firsttime) then

                Firsttime = .False.

                ! open file
                call get_environment_variable('glacier', glacier)
                open(10,file='dems/' // trim(glacier) // '/VDEM.xy')
                Read(10,*) nx
                Read(10,*) ny
                allocate(xx(nx), yy(ny))
                Allocate(dem(nx, ny))
                Do i = 1, nx
                   Do j = 1, ny
                      read(10,*) xx(i), yy(j), dem(i,j)
                   End Do
                End do
                close(10)
        End if

        ! position current point
        x = Model % Nodes % x (nodenumber)
        y = Model % Nodes % y (nodenumber)

        U = LinearInterp(dem, xx, yy, nx, ny, x, y)

        Return 
        End


        !------------------------------------------------------------------!
        FUNCTION UBIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp),allocatable :: dem(:,:), xx(:), yy(:)
        Real(kind=dp) :: x, y
        Real(kind=dp), external :: LinearInterp

        integer :: nx, ny
        integer :: i, j

        character(len=16) :: glacier

        logical :: Firsttime = .true.

        SAVE dem, xx, yy, nx, ny
        SAVE Firsttime

        if (Firsttime) then

                Firsttime = .False.

                call get_environment_variable('glacier', glacier)

                ! open file
                open(10,file='dems/' // trim(glacier) // '/UBDEM.xy')
                Read(10,*) nx
                Read(10,*) ny
                allocate(xx(nx), yy(ny))
                Allocate(dem(nx, ny))
                Do i = 1, nx
                   Do j = 1, ny
                      read(10,*) xx(i), yy(j), dem(i, j)
                   End Do
                End do
                close(10)
        End if

        ! position current point
        x = Model % Nodes % x (nodenumber)
        y = Model % Nodes % y (nodenumber)

        U = LinearInterp(dem, xx, yy, nx, ny, x, y)

        Return 
        End



        !------------------------------------------------------------------!
        FUNCTION VBIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp), allocatable :: dem(:,:), xx(:), yy(:)
        Real(kind=dp) :: x, y
        Real(kind=dp), external :: LinearInterp

        integer :: nx, ny
        integer :: i, j

        character(len=16) :: glacier

        logical :: Firsttime = .true.

        SAVE dem, xx, yy, nx, ny
        SAVE Firsttime

        if (Firsttime) then

                Firsttime = .False.

                ! open file
                call get_environment_variable('glacier', glacier)
                open(10,file='dems/' // trim(glacier) // '/VBDEM.xy')
                Read(10,*) nx
                Read(10,*) ny
                allocate(xx(nx), yy(ny))
                Allocate(dem(nx, ny))
                Do i = 1, nx
                   Do j = 1, ny
                      read(10,*) xx(i), yy(j), dem(i, j)
                   End Do
                End do
                close(10)
        End if

        ! position current point
        x = Model % Nodes % x (nodenumber)
        y = Model % Nodes % y (nodenumber)

        U = LinearInterp(dem, xx, yy, nx, ny, x, y)

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

        Real(kind=dp),allocatable :: dem(:,:), xx(:), yy(:)
        Real(kind=dp) :: x, y
        Real(kind=dp), external :: LinearInterp

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
        FUNCTION betaIni( Model, nodenumber, dumy) RESULT(U)               !
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

                call get_environment_variable('glacier', glacier)

        ! open file
                open(10,file='dems/'//trim(glacier)//'/betaDEM.xy')
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

        U = LinearInterp(dem,xx,yy,nx,ny,x,y)

        Return 
        End



        !------------------------------------------------------------------!
        FUNCTION UWa( Model, nodenumber, dumy) RESULT(U)                   !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp) :: x, y, z, zs, zb, us, ub
        Real(kind=dp), external :: USIni, UBIni, zsIni, zbIni

        ! position current point
        x=Model % Nodes % x (nodenumber)
        y=Model % Nodes % y (nodenumber)
        ! Get the height of the current point too
        z=Model % Nodes % z (nodenumber)

        zs = zsIni( Model, nodenumber, dumy )
        zb = zbIni( Model, nodenumber, dumy )

        us = USIni( Model, nodenumber, dumy )
        ub = UBIni( Model, nodenumber, dumy )

        U = ub + (1.0_dp - ((zs - z) / (zs - zb))**4) * (us - ub)

        Return 
        End


        !------------------------------------------------------------------!
        FUNCTION VWa( Model, nodenumber, dumy) RESULT(U)                   !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp) :: x, y, z, zs, zb, vs, vb
        Real(kind=dp), external :: VSIni, VBIni, zsIni, zbIni

        ! position current point
        x=Model % Nodes % x (nodenumber)
        y=Model % Nodes % y (nodenumber)
        ! Find the height of the current point
        z=Model % Nodes % z (nodenumber)

        zs = zsIni( Model, nodenumber, dumy )
        zb = zbIni( Model, nodenumber, dumy )

        vs = VSIni( Model, nodenumber, dumy )
        vb = VBIni( Model, nodenumber, dumy )

        U = vb + (1.0_dp - ((zs - z) / (zs - zb))**4) * (vs - vb)

        Return 
        End



        !------------------------------------------------------------------!
        Function MuIni( Model, nodenumber, dumy) RESULT(U)                 !
        !------------------------------------------------------------------!
        USE types

        implicit none
        TYPE(Model_t) :: Model
        Real(kind=dp) :: dumy,U
        INTEGER :: nodenumber

        Real(kind=dp), allocatable :: dem(:,:,:), xx(:), yy(:)
        Real(kind=dp) :: LinearInterp

        integer :: nx, ny, nz
        integer :: i, j, k

        character(len=16) :: glacier

        logical :: Firsttime = .true.

        Real(kind=dp) :: x, y, z, zs, zb, dz

        SAVE dem, xx, yy, nx, ny
        SAVE Firsttime

        if (Firsttime) then
            Firsttime = .false.

            call get_environment_variable('glacier', glacier)

            open(10, file = 'dems/' // trim(glacier) // '/ADEM.xy')
            Read(10, *) nx
            Read(10, *) ny
            Read(10, *) nz

            allocate(xx(nx), yy(ny))
            allocate(dem(nx, ny, nz))

            do i = 1, nx
                do j = 1, ny
                    read(10, *) xx(i), yy(j), dem(i, j, :)
                End do
            End do

            close(10)
        End if

        x = Model % Nodes % x (nodenumber)
        y = Model % Nodes % y (nodenumber)
        z = Model % Nodes % z (nodenumber)

        z = max(zb + 0.5, z)
        z = min(zs - 0.5, z)

        zs = zsIni( Model, nodenumber, dumy )
        zb = zbIni( Model, nodenumber, dumy )

        dz = (zb - zs) / nz

        k = int( (z - zb) / (zs - zb) * nz) + 1

        alpha = (z - (zb + (k - 1) * dz)) / dz
        U = (1 - alpha) * LinearInterp(dem(:,:,k), xx, yy, nx, ny, x, y) &
              & + alpha * LinearInterp(dem(:,:,k+1), xx, yy, nx, ny, x, y)

        Return
        End



        !------------------------------------------------------------------!
        include 'Interp.f90'                                               !
        !------------------------------------------------------------------!
