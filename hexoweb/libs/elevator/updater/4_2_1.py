"""Secret-key migration now runs from BootstrapMiddleware at request time.

Importing an updater during build-time Django checks must not call Vercel.
UPDATE_FROM is an application version, not a secret-key migration marker.
"""
