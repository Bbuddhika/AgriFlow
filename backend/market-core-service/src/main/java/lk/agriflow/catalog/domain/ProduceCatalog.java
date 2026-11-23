package lk.agriflow.catalog.domain;

import java.util.List;

public interface ProduceCatalog {
    List<ProduceType> findActive();
}
