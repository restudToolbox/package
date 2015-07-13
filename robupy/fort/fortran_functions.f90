!*******************************************************************************
!*******************************************************************************
!
! Development Notes:
!
!     Future releases of the GFORTRAN compiler will allow to assign NAN 
!     directly using the IEEE_ARITHMETIC module.
!
!*******************************************************************************
!*******************************************************************************
SUBROUTINE simulate_emax(emax_simulated, payoffs_ex_post, future_payoffs, & 
                num_periods, num_draws, period, k, eps_relevant, & 
                payoffs_ex_ante, edu_max, edu_start, emax, states_all, & 
                mapping_state_idx, delta)

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT)   :: payoffs_ex_post(4)
    DOUBLE PRECISION, INTENT(OUT)   :: emax_simulated
    DOUBLE PRECISION, INTENT(OUT)   :: future_payoffs(4)

    DOUBLE PRECISION, INTENT(IN)    :: payoffs_ex_ante(:)
    DOUBLE PRECISION, INTENT(IN)    :: eps_relevant(:,:)
    DOUBLE PRECISION, INTENT(IN)    :: emax(:,:)
    DOUBLE PRECISION, INTENT(IN)    :: delta

    INTEGER, INTENT(IN)             :: mapping_state_idx(:,:,:,:,:)
    INTEGER, INTENT(IN)             :: states_all(:,:,:)
    INTEGER, INTENT(IN)             :: period
    INTEGER, INTENT(IN)             :: num_periods
    INTEGER, INTENT(IN)             :: num_draws
    INTEGER, INTENT(IN)             :: k
    INTEGER, INTENT(IN)             :: edu_max
    INTEGER, INTENT(IN)             :: edu_start

!-------------------------------------------------------------------------------
! Algorithm
!-------------------------------------------------------------------------------

    CALL simulate_emax_lib(emax_simulated, payoffs_ex_post, future_payoffs, & 
                num_periods, num_draws, period, k, eps_relevant, & 
                payoffs_ex_ante, edu_max, edu_start, emax, states_all, & 
                mapping_state_idx, delta)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE calculate_payoffs_ex_ante(period_payoffs_ex_ante, num_periods, &
              states_number_period, states_all, edu_start, coeffs_A, & 
              coeffs_B, coeffs_edu, coeffs_home, max_states_period)

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT)   :: period_payoffs_ex_ante(num_periods, &
                                            max_states_period, 4)

    DOUBLE PRECISION, INTENT(IN)    :: coeffs_A(:)
    DOUBLE PRECISION, INTENT(IN)    :: coeffs_B(:)
    DOUBLE PRECISION, INTENT(IN)    :: coeffs_edu(:)
    DOUBLE PRECISION, INTENT(IN)    :: coeffs_home(:)

    INTEGER, INTENT(IN)             :: num_periods
    INTEGER, INTENT(IN)             :: states_number_period(:)
    INTEGER, INTENT(IN)             :: states_all(:,:,:)
    INTEGER, INTENT(IN)             :: edu_start
    INTEGER, INTENT(IN)             :: max_states_period

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------
    
    CALL calculate_payoffs_ex_ante_lib(period_payoffs_ex_ante, num_periods, &
              states_number_period, states_all, edu_start, coeffs_A, & 
              coeffs_B, coeffs_edu, coeffs_home, max_states_period)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE get_future_payoffs(future_payoffs, edu_max, edu_start, & 
                mapping_state_idx, period, emax, k, states_all)

    ! Development Notes:
    !
    !    This subroutine is just a wrapper to the corresponding function in the 
    !    ROBUPY library. This is required as it is used by other subroutines 
    !    in this front-end module.
    !

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT)   :: future_payoffs(4)

    DOUBLE PRECISION, INTENT(IN)    :: emax(:, :)

    INTEGER, INTENT(IN)             :: k
    INTEGER, INTENT(IN)             :: period
    INTEGER, INTENT(IN)             :: edu_max
    INTEGER, INTENT(IN)             :: edu_start
    INTEGER, INTENT(IN)             :: states_all(:, :,: )
    INTEGER, INTENT(IN)             :: mapping_state_idx(:, :, :, :, :)

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------
    
    CALL get_future_payoffs_lib(future_payoffs, edu_max, edu_start, & 
            mapping_state_idx, period,  emax, k, states_all)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE determinant(det, A)

    ! Development Notes:
    !
    !    This subroutine is just a wrapper to the corresponding function in the
    !    ROBUPY library. This is required as it is used by other subroutines
    !    in this front-end module.
    !

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT)   :: det

    DOUBLE PRECISION, INTENT(IN)    :: A(:, :)

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    det = det_lib(A)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE inverse(inv, A, n)

    ! Development Notes:
    !
    !    This subroutine is just a wrapper to the corresponding function in the
    !    ROBUPY library. This is required as it is used by other subroutines
    !    in this front-end module.
    !

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT)   :: inv(n, n)

    DOUBLE PRECISION, INTENT(IN)    :: A(:, :)

    INTEGER(our_int), INTENT(IN)    :: n

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    ! Get inverse
    inv = inverse_lib(A, n)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE trace(rslt, A)

    ! Development Notes:
    !
    !    This subroutine is just a wrapper to the corresponding function in the
    !    ROBUPY library. This is required as it is used by other subroutines
    !    in this front-end module.
    !

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT) :: rslt

    DOUBLE PRECISION, INTENT(IN)  :: A(:,:)

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    rslt = trace_fun(A)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE divergence(div, x, cov, level)

    !/* external libraries    */

    USE robupy_library

    !/* setup    */

    IMPLICIT NONE

    !/* external objects    */

    DOUBLE PRECISION, INTENT(OUT)   :: div

    DOUBLE PRECISION, INTENT(IN)    :: x(2)
    DOUBLE PRECISION, INTENT(IN)    :: cov(4,4)
    DOUBLE PRECISION, INTENT(IN)    :: level

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    CALL divergence_lib(div, x, cov, level)

END SUBROUTINE