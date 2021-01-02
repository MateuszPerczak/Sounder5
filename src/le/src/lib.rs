extern crate levenshtein;
use levenshtein::levenshtein;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

/// function compare takes two strings to campare and returns boolean value depending on set distance
#[pyfunction]
fn compare(pattern: String, string: String, distance: usize) -> PyResult<bool> {
    let counted_distance: usize = levenshtein(&pattern, &string);
    Ok(counted_distance <= distance)
}

#[pymodule]
fn le(python: Python, module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(compare, module)?)?;
    python.run("\
import sys
sys.modules['le.compare'] = compare
    ", None, Some(module.dict()))?;
    Ok(())
}
