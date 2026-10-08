# Setting Up Apache AGE with LightRAG

This document explains how to configure Apache AGE in PostgreSQL so that LightRAG (or any other application) can use AGE to store and query graph data. It covers installation, user permissions, and how to ensure the extension is loaded correctly without requiring superuser privileges at runtime.

---

## 1. Install PostgreSQL and Apache AGE

1. Make sure you have PostgreSQL 11 or higher (often 14+).  
2. Install or compile Apache AGE for your specific Postgres version.  
   - Follow official Apache AGE instructions or a community build (e.g., from GitHub or a release for Windows, Mac, Linux).

---

## 2. Enable AGE at the Server Level

In many environments, you should add “age” to the server’s shared_preload_libraries. This ensures Postgres loads it automatically at startup. For example, in (macOS/Homebrew) /opt/homebrew/var/postgresql@14/postgresql.conf:
```
shared_preload_libraries = 'age'
```

After editing postgresql.conf, restart PostgreSQL so the changes take effect:

• macOS/Homebrew:
  brew services restart postgresql@14

• Linux system service:
  sudo systemctl restart postgresql

---

## 3. Create the “age” Extension in Your Target Database

Extensions in Postgres are installed per-database. If you want to use “lr_hello_world” as your main database, connect to it as a superuser:

```
psql --username tim --dbname lr_hello_world
```

Then run:

```
CREATE EXTENSION IF NOT EXISTS age;
```

You can confirm by running \dx in psql. You should see “age” listed among installed extensions.  

---

## 4. Grant Privileges to Other Users (e.g., “lr”)

If you plan to run queries from a lower-privilege user, such as “lr,” you need to grant several permissions. While connected as a superuser, run these commands:

```sql
-- Grant usage on the schema
GRANT USAGE ON SCHEMA ag_catalog TO lr;

-- Grant access to ag_graph table
GRANT ALL PRIVILEGES ON TABLE ag_catalog.ag_graph TO lr;

-- Grant access to ag_label table
GRANT ALL PRIVILEGES ON TABLE ag_catalog.ag_label TO lr;

-- Grant execute permission on functions in ag_catalog
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ag_catalog TO lr;

-- If using sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ag_catalog TO lr;

-- Additional permissions that might be needed
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ag_catalog TO lr;
```

These permissions ensure that the "lr" user can:
- Access the AGE schema
- Create and manage graphs
- Read and write to the necessary AGE tables
- Execute AGE functions
- Use sequences for ID generation

---

## 5. Verify That “lr” Can Create and Access Graphs

Still in psql—now as user “lr,” connect to the same database:

```
psql --username lr --dbname lr_hello_world
```

Try creating a graph:

```
SET search_path = ag_catalog, "$user", public;
SELECT create_graph('test_graph');
```

You should see:

```
NOTICE:  graph "test_graph" has been created
 create_graph 
--------------
 
(1 row)
```

If it says “graph already exists,” that’s fine—it means it’s recognized by your user.  

No “LOAD 'age'” or “CREATE EXTENSION age” calls are needed at runtime if the extension is already set up.  

---

## 6. Adjusting or Removing LOAD 'age' Calls in the Code

In various LightRAG modules (e.g., postgres_impl.py or age_impl.py), you might see code lines like:

```
await conn.execute("LOAD 'age'");
await conn.execute("CREATE EXTENSION age;"); 
```
  
• LOAD 'age' requires superuser privileges unless you have a special environment or you’ve put “age” in shared_preload_libraries.  
• CREATE EXTENSION age also requires superuser privileges to install C-language extensions.  

If you have already installed the extension as a superuser and configured shared_preload_libraries='age', you can remove/comment out those lines. Your non-superuser “lr” won’t need to do them—just ensure the user sets search_path to “ag_catalog, $user, public,” has usage on the ag_catalog schema, and calls “create_graph(...)” only if it’s allowed.

---

## 7. Common Errors and Fixes

• ERROR: function create_graph(unknown) does not exist  
  - Means the AGE extension is not installed in this exact database. Install it with CREATE EXTENSION age again, specifically in the database you’re connected to.

• ERROR: extension “age” must be created by a superuser  
  - Installing a C-language extension requires a superuser role. Use your Postgres superuser, e.g., “tim.”

• ERROR: access to library “age” is not allowed  
  - Happens when a lower-privilege user calls LOAD 'age'. Remove or skip that call, or give that user superuser privileges.  

• NOTICE: graph “test_graph” has been created  
  - A success message indicating your user can create or reference that graph.

---

## 8. Putting It All Together

Below is a typical procedure on a fresh setup:

1. Edit postgresql.conf to have shared_preload_libraries = 'age'.  
2. Restart PostgreSQL.  
3. Connect as superuser to your target DB:  
   psql --username tim --dbname lr_hello_world  
   Run:  
     CREATE EXTENSION IF NOT EXISTS age;  
     GRANT USAGE ON SCHEMA ag_catalog TO lr;  
4. Connect as user lr:  
   psql --username lr --dbname lr_hello_world  
   SET search_path = ag_catalog, "$user", public;  
   SELECT create_graph('example_graph');  
5. In your LightRAG code, remove or bypass lines that do CREATE EXTENSION or LOAD 'age' at runtime, unless you really need them.  

After these steps, your “lr” user can run PARALLEL queries, match, merge, or any other AGE-based Cypher queries with minimal friction. This ensures you will not encounter permission errors or missing function errors.

---

**That’s it!** You’re now set up to use Apache AGE in your PostgreSQL database with LightRAG. Feel free to extend these instructions with details specific to your environment. 
