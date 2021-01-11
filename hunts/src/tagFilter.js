function getDescendants(tableRow) {
  const allChildren = [tableRow];
  for (let i = 0; i < allChildren.length; i++) {
    const current = allChildren[i];
    Array.prototype.push.apply(allChildren, current.subRows);
  }
  return allChildren;
}

function isMatchingTagInFilter(tagList, tag) {
  return tagList.find(x => ['name', 'color', 'id'].every(key => x[key] === tag[key]));
}

function filterWithTagAdded(tagList, tag) {
  return tagList.concat([tag]);
}

export function filterWithTagRemoved(tagList, tag) {
  return tagList.filter(x => !(['name', 'color', 'id'].every(key => x[key] === tag[key])));
}

export function filterWithTagToggled(tagList, tag) {
  // Returns a version of the filter tag list with the tag added
  // if the tag is not in the filter already, otherwise returns
  // a version with the tag removed.
  return isMatchingTagInFilter(tagList, tag) ? filterWithTagRemoved(tagList, tag) : filterWithTagAdded(tagList, tag);
}

export function filterPuzzlesByTagFn(rows, id, tagList) {
  return rows.filter((row) => {
    return tagList.length === 0 || tagList.some(tag => row.original.tags.map(x => x.id).includes(tag.id));
  });
}
