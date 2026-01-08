# GitHub Actions Workflow Reference

## Workflow File Structure

```yaml
name: Workflow Name

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  GLOBAL_VAR: value

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Step name
        run: command
```

## Common Triggers

### Push Events

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'
    paths:
      - 'src/**'
      - '!docs/**'
    tags:
      - 'v*'
```

### Pull Request Events

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]
```

### Scheduled Events

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
```

### Manual Trigger

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
```

## Job Configuration

### Matrix Strategy

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20, 22]
        exclude:
          - os: windows-latest
            node: 18
    runs-on: ${{ matrix.os }}
```

### Job Dependencies

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps: [...]
```

### Conditional Execution

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
```

## Caching

### Node.js

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
```

### Python

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

### Rust

```yaml
- uses: Swatinem/rust-cache@v2
```

### Custom Cache

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache
      node_modules
    key: ${{ runner.os }}-${{ hashFiles('**/lockfile') }}
    restore-keys: |
      ${{ runner.os }}-
```

## Security Scanning

### CodeQL Analysis

```yaml
- uses: github/codeql-action/init@v3
  with:
    languages: javascript, python

- uses: github/codeql-action/analyze@v3
```

### Dependency Review

```yaml
- uses: actions/dependency-review-action@v4
```

### Secret Scanning

```yaml
- uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
```

## Artifacts and Releases

### Upload Artifacts

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 5
```

### Create Release

```yaml
- uses: softprops/action-gh-release@v2
  with:
    files: |
      dist/*.zip
      dist/*.tar.gz
    generate_release_notes: true
```

## Environment and Secrets

### Using Secrets

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}

steps:
  - run: echo "Token: ${{ secrets.GITHUB_TOKEN }}"
```

### Environment Protection

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://example.com
```

## Reusable Workflows

### Calling Reusable Workflow

```yaml
jobs:
  call-workflow:
    uses: ./.github/workflows/reusable.yml
    with:
      config-path: .github/config.json
    secrets:
      token: ${{ secrets.TOKEN }}
```

## Best Practices

- Use specific action versions: `actions/checkout@v4` not `@main`
- Enable fail-fast for matrix: Stop all jobs if one fails
- Cache dependencies: Reduce build times significantly
- Use concurrency: Cancel redundant workflow runs
- Minimize secrets exposure: Use OIDC when possible
- Add timeout: Prevent hung jobs

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    timeout-minutes: 30
```
