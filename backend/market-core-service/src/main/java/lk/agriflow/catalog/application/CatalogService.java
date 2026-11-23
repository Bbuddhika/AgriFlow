package lk.agriflow.catalog.application;

import java.util.List;
import lk.agriflow.catalog.domain.ProduceCatalog;
import lk.agriflow.catalog.domain.ProduceType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CatalogService {
    private final ProduceCatalog catalog;

    public CatalogService(ProduceCatalog catalog) { this.catalog = catalog; }

    @Transactional(readOnly = true)
    public List<ProduceType> listActive() { return catalog.findActive(); }
}
