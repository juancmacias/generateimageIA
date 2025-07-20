-- setup_database.sql - Script para crear las tablas necesarias en Supabase

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    api_key_hash VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    usage_limit INTEGER DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    last_used TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_api_key_hash ON users(api_key_hash);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Crear tabla de generaciones de imágenes (para auditoría y estadísticas)
CREATE TABLE IF NOT EXISTS image_generations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    num_inference_steps INTEGER NOT NULL,
    guidance_scale DECIMAL(4,2) NOT NULL,
    generation_time DECIMAL(8,2),
    filename VARCHAR(255),
    device VARCHAR(50),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear índices para la tabla de generaciones
CREATE INDEX IF NOT EXISTS idx_image_generations_user_id ON image_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_image_generations_created_at ON image_generations(created_at);
CREATE INDEX IF NOT EXISTS idx_image_generations_success ON image_generations(success);

-- Crear tabla de API keys (para múltiples claves por usuario)
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL DEFAULT 'Default API Key',
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Crear índices para API keys
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);

-- Crear función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para actualizar updated_at en la tabla users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Crear vista para estadísticas de usuario
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.usage_count,
    u.usage_limit,
    u.created_at as user_created_at,
    u.last_login,
    u.last_used,
    COUNT(ig.id) as total_generations,
    COUNT(CASE WHEN ig.success = true THEN 1 END) as successful_generations,
    COUNT(CASE WHEN ig.success = false THEN 1 END) as failed_generations,
    AVG(CASE WHEN ig.success = true THEN ig.generation_time END) as avg_generation_time,
    MAX(ig.created_at) as last_generation_date
FROM users u
LEFT JOIN image_generations ig ON u.id = ig.user_id
GROUP BY u.id, u.email, u.full_name, u.usage_count, u.usage_limit, 
         u.created_at, u.last_login, u.last_used;

-- Crear política de seguridad RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE image_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- IMPORTANTE: Política para permitir registro público de nuevos usuarios
CREATE POLICY "Allow public registration" ON users
    FOR INSERT WITH CHECK (true);

-- Política para que los usuarios solo vean sus propios datos
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id OR auth.role() = 'service_role');

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id OR auth.role() = 'service_role');

CREATE POLICY "Users can view own generations" ON image_generations
    FOR SELECT USING (auth.uid() = user_id OR auth.role() = 'service_role');

CREATE POLICY "Users can insert own generations" ON image_generations
    FOR INSERT WITH CHECK (auth.uid() = user_id OR auth.role() = 'service_role');

CREATE POLICY "Users can view own api keys" ON api_keys
    FOR SELECT USING (auth.uid() = user_id OR auth.role() = 'service_role');

CREATE POLICY "Users can manage own api keys" ON api_keys
    FOR ALL USING (auth.uid() = user_id OR auth.role() = 'service_role');

-- Insertar usuario de prueba (opcional, comentar en producción)
-- INSERT INTO users (email, password_hash, full_name, api_key_hash, usage_limit) 
-- VALUES (
--     'test@example.com',
--     '$2b$12$example_hash', -- Reemplazar con hash real
--     'Usuario de Prueba',
--     'hash_of_api_key', -- Reemplazar con hash real
--     1000
-- ) ON CONFLICT (email) DO NOTHING;

-- Comentarios sobre el esquema
COMMENT ON TABLE users IS 'Tabla de usuarios del sistema de generación de imágenes';
COMMENT ON TABLE image_generations IS 'Registro de todas las generaciones de imágenes realizadas';
COMMENT ON TABLE api_keys IS 'Claves API para acceso programático';
COMMENT ON VIEW user_stats IS 'Vista con estadísticas agregadas por usuario';

-- Función para limpiar generaciones antiguas (opcional)
CREATE OR REPLACE FUNCTION cleanup_old_generations(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM image_generations 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas de uso
CREATE OR REPLACE FUNCTION get_usage_stats()
RETURNS TABLE (
    total_users BIGINT,
    active_users BIGINT,
    total_generations BIGINT,
    successful_generations BIGINT,
    avg_generation_time DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM users)::BIGINT as total_users,
        (SELECT COUNT(*) FROM users WHERE is_active = true)::BIGINT as active_users,
        (SELECT COUNT(*) FROM image_generations)::BIGINT as total_generations,
        (SELECT COUNT(*) FROM image_generations WHERE success = true)::BIGINT as successful_generations,
        (SELECT AVG(generation_time) FROM image_generations WHERE success = true)::DECIMAL as avg_generation_time;
END;
$$ LANGUAGE plpgsql;
