# Interpolation 
* export data for each measurement will be in the form
frequency (x) - intensity f(x)

* Suppose that there exists a continuous function f(x) where x is the frequency from a set of real numbers $x\in \mathbb{R}$.
* Call the set of points at which the machine measures the value of $f(x): x \in KFx \subset \mathbb{R}$ where $KFx= KnowFx= {x_0, ....,x_N}$ a discrete set of known data points.
* We only know the value of $f(x): x \in KFx$ (the frequency point measured by the machine),
  so there will be a lot of unknown values $f(\hat{x}): \hat{x} \in uKFx$ with $uKFx = UnknownFx = \mathbb{R} \setminus KFx$.
* To find unknown values $f(\hat{x})$, we use interpolation. 
* Interpolation is a type of estimation, a method of constructing (finding) new data points based on the range of a discrete set of known data points. Data points from the original function can be interpolated to produce a simpler function which is still fairly close to the original. 
* Let  $\tilde{f}(x)$ be our approximation function.
  * the unknown values $f(\hat{x}) \approx \tilde{f}(\hat{x})$ where  $\hat{x} \in uKFx$
  * and also satisfied $f(x) = \tilde{f}(x)$ where $x \in KFx$ (the  original data points from each measurement will not be manupalated)

## for example:
I make up a dataset:

| frequency (x)| intensity f(x) |
| ----------- | ----------- |
| -3      | 9       |
| -2   | 4        |
| -1   | 1        |
| 0   | 0        |
|1   | 1        |
| 2   | 4        |
| 3   | 9        |

* Interpolation provides a means of estimating the function at intermediate points, such as $x= 2.5$

* There some methods of interpolation, differing in such properties as: accuracy, cost, number of data points needed, and smoothness of the resulting interpolant function. 

In our case we use Cubic Spline Interpolation. 
```
class scipy.interpolate.interp1d(x, y, kind='cubic')
see [store_results.interpolation_datadict]
tem_f = interp1d(tem_x, tem_y, kind="cubic")
```

* Cubic spline interpolation is a special case for Spline interpolation that is used very often to avoid the problem of Runge's phenomenon. 
* This method gives an interpolating polynomial that is smoother and has smaller error than some other interpolating polynomials such as Lagrange polynomial and Newton polynomial.

# Numerical integration
* we also use our interpolation function $\tilde{f}(x)$ for the numerical integration task (compute peak area)
* for example:
    we want to have peak area of any intervall $[x_1,x_2]$, we have
	$$PeakArea =  \int_{x_1}^{x_2} \tilde{f}(x) \,dx$$
* There are also some methods of numerical integral. In our case, we use Gaussian quadrature,which estimates integrals using numerical quadrature.
```
scipy.integrate.quad(func, a, b)
see [peak_area.compute_single_peak_area]
peak_area = np.abs(
            quad(f, chemical_shift.ppmstr, chemical_shift.ppmend))
```

