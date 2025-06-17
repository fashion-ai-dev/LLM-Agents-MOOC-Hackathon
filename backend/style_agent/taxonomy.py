from json import JSONEncoder
from typing import Dict, List, Literal
from dotenv import load_dotenv
load_dotenv()


class TaxonomyCategoryVisionSchema:
    def __init__(self, property: str, description: str):
        self.property = property
        self.description = description


class TaxonomyCategoryMethodologySchemaPropertyItem:
    def __init__(self, t_type: str):
        self.type = t_type

    def to_dict(self):
        return {
            "type": self.type,
        }


class TaxonomyCategoryMethodologySchemaProperty:
    def __init__(
        self,
        t_type: str,
        description: str,
        items: TaxonomyCategoryMethodologySchemaPropertyItem = None,
    ):
        self.type = t_type
        self.description = description
        self.items = items

    def to_dict(self):
        response = {
            "type": self.type,
            "description": self.description,
        }

        if self.items is not None:
            response["items"] = self.items.to_dict()
        return response


class TaxonomyCategoryMethodologySchema:
    def __init__(
        self,
        type: str,
        required_properties: List[str] = None,
        typed_properties: Dict[str, TaxonomyCategoryMethodologySchemaProperty] = None,
        additional_properties: bool = False,
    ):
        self.type = type
        self.properties = typed_properties or {}
        self.additional_properties = additional_properties
        self.required = required_properties or []

    def add_required_property(self, p_property: str):
        self.required.append(p_property)

    def add_typed_property(
        self,
        property: str,
        t_type: str,
        description: str,
        items: TaxonomyCategoryMethodologySchemaPropertyItem = None,
    ):
        self.properties[property] = TaxonomyCategoryMethodologySchemaProperty(
            t_type, description, items
        )

    def to_dict(self):
        return {
            "type": self.type,
            "properties": {
                key: value.to_dict() for key, value in self.properties.items()
            },
            "required": self.required,
            "additionalProperties": self.additional_properties,
        }


class TaxonomyCategoryMethodology:
    def __init__(self, name: str, schema: TaxonomyCategoryMethodologySchema):
        self.name = name
        self.schema = schema

    def to_dict(self):
        return {
            "name": self.name,
            "schema": self.schema.to_dict(),
        }


class TaxonomyCategoryProperties:
    def __init__(
        self,
        type: str,
        property: str,
        description: str,
        examples: str,
        property_order: int,
    ):
        self.type = type
        self.property = property
        self.description = description
        self.examples = examples
        self.property_order = property_order

    def to_dict(self):
        return self.__dict__


class TaxonomyCategory:
    def __init__(self, name: str, properties: List[TaxonomyCategoryProperties]):
        self.name = name
        self.properties = properties

    def get_characteristic_attributes(self):
        return [prop for prop in self.properties if prop.type in ["design_features"]]

    def get_common_attributes(self):
        return [
            prop
            for prop in self.properties
            if prop.type
            in [
                "prints_and_colors",
                "sales_support",
                "estampa_e_cores",
                "suporte_a_vendas",
            ]
        ]

    def get_methodology_object(self) -> TaxonomyCategoryMethodology:
        taxonomy_schema = TaxonomyCategoryMethodologySchema("object")

        for m_property in self.properties:
            name = m_property.property
            description = m_property.description

            if name and description:
                t_prop = "string" if name != "images_alt_text" else "array"
                items = (
                    TaxonomyCategoryMethodologySchemaPropertyItem("string")
                    if t_prop == "array"
                    else None
                )
                taxonomy_schema.add_typed_property(name, t_prop, description, items)
                taxonomy_schema.add_required_property(name)

        result = TaxonomyCategoryMethodology("methodology", taxonomy_schema)

        return result

    # def get_vision_taxonomy_object(self) -> List[TaxonomyCategoryVisionSchema]:
    #     result = []

    #     for prop in self.properties:
    #         name, examples, description = prop.property, prop.examples, prop.description

    #         if examples and pd.notna(examples):
    #             description = f"{description}: {examples}"

    #         result.append(TaxonomyCategoryVisionSchema(name, description))

    #     return result

    def get_by_property(self, property: str) -> TaxonomyCategoryProperties:
        for prop in self.properties:
            if prop.property == property:
                return prop

    def to_dict(self):
        return {
            "name": self.name,
            "properties": [prop.to_dict() for prop in self.properties],
        }


class Taxonomy:
    def __init__(self, categories: List[TaxonomyCategory]):
        self.categories = categories

    def get_by_category_name(self, category_name: str) -> TaxonomyCategory:
        for category in self.categories:
            if category.name == category_name:
                return category

    def get_by_categories_list(self, category_list: List[str]) -> "Taxonomy":
        return Taxonomy.create_by_taxonomy_categories(
            [
                category
                for category in self.categories
                if category.name in category.name in category_list
            ]
        )

    def get_categories(self) -> List[TaxonomyCategory]:
        return self.categories

    def get_categories_name(self) -> List[str]:
        return [category.name for category in self.categories]

    def get_common_attributes(self) -> TaxonomyCategoryProperties:
        return self.categories[0].get_common_attributes()

    @staticmethod
    def create(taxonomy_json: List[dict]) -> "Taxonomy":
        categories = []

        for category in taxonomy_json:
            properties = []

            for prop in category["properties"]:
                properties.append(
                    TaxonomyCategoryProperties(
                        prop["group"],
                        prop["property"],
                        prop["description"],
                        prop["examples"],
                        prop["property_order"],
                    )
                )

            categories.append(TaxonomyCategory(category["name"], properties))

        return Taxonomy(categories)

    @staticmethod
    def create_by_taxonomy_categories(
        taxonomy_categories: List[TaxonomyCategory],
    ) -> "Taxonomy":
        return Taxonomy(taxonomy_categories)
