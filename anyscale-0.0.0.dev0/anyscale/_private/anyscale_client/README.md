# Anyscale Client

This directory contains a client wrapper that should be used for all communication with the Anyscale HTTP REST API.
The purpose of centralizing this logic is to:

- Avoid duplicating code.
- Keep all external dependencies in one place.
- Enable writing comprehensive unit tests for upstream components (without using mocks!) using the `FakeAnyscaleClient`.

## Testing

The `AnyscaleClient` is tested using a fake version of the internal and external OpenAPI clients.

Upstream components should use the `FakeAnyscaleClient` to write their tests.
This client should mirror the behavior of the real `AnyscaleClient` as closely as possible (avoid making methods and functionality
complete "dummies").
