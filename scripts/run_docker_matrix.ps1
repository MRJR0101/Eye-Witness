param(
    [string[]]$Versions = @("3.10", "3.11", "3.12", "3.13")
)

$ErrorActionPreference = "Stop"

foreach ($v in $Versions) {
    $tag = "eye-witness-matrix:$($v.Replace('.', '-'))"
    Write-Host "== Building and testing Python $v =="
    docker build `
        --build-arg PYTHON_VERSION=$v `
        -f docker/matrix/Dockerfile `
        -t $tag `
        .
    docker run --rm $tag
}

Write-Host "Matrix run completed."
