import scrapy

class PokeDataSpider(scrapy.Spider):
    name = 'poke_data_spider'
    base_url = "https://pokemondb.net/"

    start_urls = ["https://pokemondb.net/pokedex/all"]

    def parse(self, response):
        rows = response.css('#pokedex > tbody > tr')
        for row in rows:
            detail_page = row.css("td.cell-name > a::attr(href)").extract_first()
            yield response.follow(self.base_url + detail_page, self.extract_pokemon_details)

    def extract_pokemon_details(self, response):
        # Coletar URL da página do Pokémon
        current_page_url = response.url

        # Coletar informações sobre evoluções
        evolution_data = []
        evolution_entries = response.css('.infocard-list-evo .infocard')
        for entry in evolution_entries:
            evolution_title = entry.css('a.ent-name::text').get()
            evolution_id = entry.css('.text-muted::text').get()  # Captura o número da evolução
            evolution_link = response.urljoin(entry.css('a.ent-name::attr(href)').get())
            if evolution_title and evolution_id:
                evolution_data.append({
                    'id': evolution_id.strip(),
                    'name': evolution_title,
                    'url': evolution_link
                })

        # Coletar habilidades
        ability_data = []
        ability_entries = response.css('.vitals-table tr:contains("Abilities") td a')
        for entry in ability_entries:
            ability_title = entry.css('::text').get()
            ability_link = response.urljoin(entry.css('::attr(href)').get())
            ability_data.append({
                'name': ability_title,
                'url': ability_link
            })

        yield {
            'id': response.css('.vitals-table > tbody > tr:nth-child(1) > td > strong::text').get(),
            'name': response.css('#main > h1::text').get(),
            'height_cm': response.css('.vitals-table > tbody > tr:nth-child(4) > td::text').get().strip(),
            'weight_kg': response.css('.vitals-table > tbody > tr:nth-child(5) > td::text').get().strip(),
            'type_list': ', '.join(response.css('.vitals-table > tbody > tr:nth-child(2) > td > a::text').getall()),
            'abilities': ability_data,
            'evolutions': evolution_data,
            'page_url': current_page_url,
        }
