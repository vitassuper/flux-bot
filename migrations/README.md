# Alembic

Alembic is a database migration tool for SQLAlchemy.

## Usage

Once you have created the configuration file and migration script directory, you can use Alembic to manage your database migrations.

Here are some of the most commonly used commands:

### Creating a new migration script

To create a new migration script, you can use the `alembic revision` command:

```bash
alembic revision -m "Add new table"
```

This will create a new migration script in the `migrations/versions` directory with the name `xxxxxxxxxxxx_add_new_table.py` (where `xxxxxxxxxxxx` is a timestamp).

You can then edit the migration script to define your database schema changes.

### Upgrading the database

To upgrade the database to the latest version, you can use the `alembic upgrade` command:

```bash
alembic upgrade head
```

This will apply all the migration scripts that have not yet been applied to the database.

### Downgrading the database

To downgrade the database to a previous version, you can use the `alembic downgrade` command:

```bash
alembic downgrade -1
```

This will apply the previous migration script to the database.

### Generating a SQL script

To generate a SQL script for a migration, you can use the `alembic upgrade` command with the `--sql` option:

```bash
alembic upgrade head --sql > upgrade.sql
```

This will generate a SQL script that applies all the migration scripts that have not yet been applied to the database.

### Displaying the current version

To display the current version of the database, you can use the `alembic current` command:

```bash
alembic current
```

This will display the current version of the database according to the Alembic migration scripts.

## Conclusion

Alembic is a powerful database migration tool that can help you manage your database schema changes with ease. With the commands listed above, you can create and apply migration scripts, generate SQL scripts, and more.
