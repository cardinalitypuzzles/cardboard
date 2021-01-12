export function filterWithTagToggled(tagList, tag) {
  // Returns a version of the filter tag list with the tag added
  // if the tag is not in the filter already, otherwise returns
  // a version with the tag removed.
  return tagList.map(x => x.name).includes(tag.name) ? tagList.filter(i => i.name !== tag.name) : tagList.concat([tag]);
}

export function filterPuzzlesByTagFn(rows, id, tagList) {
  return rows.filter((row) => {
    return tagList.every(tag => row.original.tags.map(x => x.id).includes(tag.id));
  });
}
