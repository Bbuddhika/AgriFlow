package lk.agriflow.catalog.api;

import java.util.List;
import lk.agriflow.catalog.application.CatalogService;
import lk.agriflow.catalog.domain.ProduceType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CatalogController {
    private final CatalogService catalog;

    public CatalogController(CatalogService catalog) { this.catalog = catalog; }

    @GetMapping("/api/v1/catalog/produce")
    public List<ProduceType> list() { return catalog.listActive(); }
}
