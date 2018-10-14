create table entries
(
	entry_id integer
		primary key
		 autoincrement,
	entry text
)
;

create table cooccurrences
(
	entry_a integer not null
		constraint cooccurrences_entries_entry_id_fk
			references entries,
	entry_b integer not null
		constraint cooccurrences_entries_entry_id_fk_2
			references entries,
	frequency integer not null,
	constraint cooccurrences_pk
		primary key (entry_a, entry_b)
)
;

create unique index entries_entry_uindex
	on entries (entry)
;

create table occurrences
(
	entry_id integer not null
		primary key
		constraint occurrences_entries_entry_id_fk
			references entries,
	frequency integer not null
)
;

create table tags
(
	tag_id integer not null
		primary key
		 autoincrement,
	tag text not null
)
;

create table prototypes
(
	tag_id integer not null
		constraint prototypes_tags_tag_id_fk
			references tags,
	prototype text not null
)
;

create table scores
(
	entry_id integer
		constraint scores_entries_entry_id_fk
			references entries,
	tag_id integer not null
		constraint scores_tags_tag_id_fk
			references tags,
	score float not null
)
;

create unique index tags_tag_uindex
	on tags (tag)
;

