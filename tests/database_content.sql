INSERT INTO public.language (id, iso693_3, name) VALUES (0, 'ara', 'Arabic');
INSERT INTO public.language (id, iso693_3, name) VALUES (1, 'eng', 'English');
INSERT INTO public.language (id, iso693_3, name) VALUES (2, 'jpn', 'Japanese');
INSERT INTO public.language (id, iso693_3, name) VALUES (3, 'fra', 'French');
INSERT INTO public.language (id, iso693_3, name) VALUES (4, 'deu', 'German');
INSERT INTO public.language (id, iso693_3, name) VALUES (5, 'spa', 'Spanish');
INSERT INTO public.language (id, iso693_3, name) VALUES (6, 'ita', 'Italian');

INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (4, 3, 77, 456963, 'Lass uns etwas versuchen!', 'Tentons quelque chose !', '{"Tentons","quelque","chose","{{c1::!}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (4, 2, 81, 4705, 'Heute ist der 18. Juni und das ist der Geburtstag von Muiriel!', '今日は６月１８日で、ムーリエルの誕生日です！', '{"今日","は","６月","１","８","日","で","{{c1::、}}","ムーリエル","の","誕生","日","です","！"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (4, 1, 89, 1288, 'Ich weiß einfach nicht, was ich sagen soll.', 'I just don''t know what to say.', '{"I","just","don''t","know","what","{{c1::to}}","say."}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (4, 5, 89, 2493, 'Ich weiß einfach nicht, was ich sagen soll.', 'Simplemente no sé qué decir...', '{"Simplemente","no","sé","{{c1::qué}}","decir..."}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (4, 3, 89, 3103, 'Ich weiß einfach nicht, was ich sagen soll.', 'Je ne sais simplement pas quoi dire...', '{"Je","{{c1::ne}}","sais","simplement","pas","quoi","dire..."}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (4, 1, 89, 693485, 'Ich weiß einfach nicht, was ich sagen soll.', 'I simply don''t know what to say...', '{"I","simply","don''t","know","{{c1::what}}","to","say..."}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 6, 6152061, 8593117, 'Is that material good?', 'Quel materiale è buono?', '{"Quel","materiale","{{c1::è}}","buono?"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 3, 6150621, 6155531, 'You don''t even know his name, do you?', 'Tu ne connais même pas son nom, n''est-ce pas ?', '{"Tu","{{c1::ne}}","connais","même","pas","son","nom","","n''est-ce","pas","?"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (5, 1, 6150613, 5734478, 'Nosotros tres permaneceremos juntos.', 'We three will stick together.', '{"We","three","{{c1::will}}","stick","together."}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 3, 6151704, 6155481, 'Is there any way you can un-shrink a T-shirt that has shrunk?', 'Existe-t-il un moyen de "dé-rétrécir" un T-shirt qui a rétréci ?', '{"Existe-t-il","{{c1::un}}","moyen","de","dé-rétrécir","un","T-shirt","qui","a","rétréci","?"}');

INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 1, 2, 'a a a', 'b b b', '{"b","b","{{c1::!}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 3, 4, 'a a c', 'b b c', '{"b","b","{{c1::ee}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 5, 6, 'c a c', 'l b c', '{"l","b","{{c1::c}}", "e"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 7, 8, 'a r c', 'b t c', '{"b","t","{{c1::c}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 9, 8, 'a r c', 'b t c', '{"b","t","{{c1::c}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 11, 12, 'a r c', 'b t c', '{"b","t","{{c1::c}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 13, 14, 'a r c', 'bf t c', '{"b","t","{{c1::c}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 15, 16, 'a rdfg c', 'b tff c', '{"bf","{{c1::c}}","{{c2::ee}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 17, 18, 'asdg r c', 'b t cw', '{"b","tee","{{c1::c}}"}');
INSERT INTO public.card (from_lang, to_lang, from_id, to_id, from_txt, original_txt, to_tokens) VALUES (1, 4, 19, 20, 'a r cdsfg', 'be te c', '{"b","t","{{c1::c}}"}');

--
INSERT INTO account(id) VALUES(1);
