package lk.agriflow.catalog.infrastructure;

import java.util.List;
import java.util.UUID;
import lk.agriflow.catalog.domain.ProduceCatalog;
import lk.agriflow.catalog.domain.ProduceType;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

@Repository
public class JdbcProduceCatalog implements ProduceCatalog {
    private final JdbcClient jdbc;

    public JdbcProduceCatalog(JdbcClient jdbc) { this.jdbc = jdbc; }

    @Override
    public List<ProduceType> findActive() {
        return jdbc.sql("SELECT id, code, name, unit FROM produce_types WHERE active = true ORDER BY name")
            .query((rs, row) -> new ProduceType(rs.getObject("id", UUID.class),
                rs.getString("code"), rs.getString("name"), rs.getString("unit")))
            .list();
    }
}
